import inspect
import pathlib

import subprocess
import urllib
import os

import logging


class CtermInterface:

    _logger = None

    def __init__(self, cterm):
        try:
            self._logger = logging.getLogger(__name__)
            cterm = pathlib.Path(cterm)
            self._process = subprocess.Popen([f'{cterm}', '-i', '-e'],
                                             stdin=subprocess.PIPE,
                                             stdout=subprocess.PIPE,
                                             stderr=subprocess.PIPE)
            ans = self._read()
            assert ans == 'hello', 'answer is incorrect, expected="hello", get="{}"'.format(ans)
        except Exception as e:
            raise Exception('{}.{}() {}: {}'.format(
                self.__class__.__name__, inspect.currentframe().f_code.co_name, e.__class__.__name__, e))

    def command(self, command, *params):
        try:
            param = '" "'.join(params)
            if param != '':
                command = command + ' ' + '"' + param + '"'
            self._write(command)
            ans = self._read()
            final_ans = self._parse_ans(ans)
            if command.startswith('post'):
                ans = self._read()
                tmp = self._parse_ans(ans)
                assert final_ans['num'] == tmp['num'], 'num is incorrect, expected="{}", get="{}"' \
                    .format(final_ans['num'], tmp['num'])
                final_ans = tmp
            return final_ans
        except Exception as e:
            if command.endswith('"app.abort"') and str(e).endswith('\'receiving data on socket failed, error 10054\''):
                return {'status': 'ok'}
            else:
                raise Exception('{}.{}({}) {}: {}'.format(
                    self.__class__.__name__, inspect.currentframe().f_code.co_name, command, e.__class__.__name__, e))

    def _read(self):
        ans = self._process.stdout.readline().decode()
        assert ans is not None, 'answer is empty'
        if 'verbose' in dir(self._logger):
            self._logger.verbose('read: {}'.format(ans))
        final_ans = urllib.parse.unquote(ans)
        final_ans = final_ans.rstrip()
        if 'verbose' in dir(self._logger):
            self._logger.verbose('ans: {}'.format(final_ans))
        return final_ans

    def _write(self, command):
        if 'verbose' in dir(self._logger):
            self._logger.verbose('write: {}'.format(bytes(command + os.linesep, encoding='utf-8')))
        self._process.stdin.write(bytes(command + os.linesep, encoding='utf-8'))
        self._process.stdin.flush()

    def _parse_ans(self, ans):
        assert ans.startswith('ok'), ans
        final_ans = {'status': ans.split(sep='\n', maxsplit=1)[0]}
        if len(ans.split(sep='\n', maxsplit=1)) == 1:
            final_ans['value'] = final_ans['status']
        else:
            if ans.split(sep='\n', maxsplit=1)[1].startswith('post') \
                    or ans.split(sep='\n', maxsplit=1)[1].startswith('send'):
                if ans.split(sep='\n', maxsplit=1)[1].startswith('post'):
                    final_ans['num'] = ans.split(sep='\n', maxsplit=1)[1].split(sep=' ', maxsplit=1)[0][4:]
                if len(ans.split(sep='\n', maxsplit=1)[1].split(sep=' ', maxsplit=1)) == 2:
                    final_ans['value'] = ans.split(sep='\n', maxsplit=1)[1].split(sep=' ', maxsplit=1)[1]
            else:
                final_ans['value'] = ans.split(sep='\n', maxsplit=1)[1]
        if 'verbose' in dir(self._logger):
            self._logger.verbose('parsed ans: {}'.format(final_ans))
        return final_ans

    def __del__(self):
        try:
            self._logger = None
            self._write('quit')
            ans = self._read()
            assert ans == 'bye', 'answer is incorrect, expected="bye", get="{}"'.format(ans)
        except Exception as e:
            raise Exception('{}.{}() {}: {}'.format(
                self.__class__.__name__, inspect.currentframe().f_code.co_name, e.__class__.__name__, e))
        finally:
            self._process.stdin.close()
            self._process.terminate()
            self._process.wait(timeout=3)
