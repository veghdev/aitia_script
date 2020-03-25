from subprocess import Popen, PIPE
from urllib.parse import unquote
from os import linesep
from inspect import currentframe

from tools.logging_tools.logger import Logger


class CtermInterface:
    _logger = None
    _process = None

    def __init__(self, app, path, logger=None):
        try:
            if logger is not None:
                self._set_logger(logger)
            self._process = Popen([f'{path}/{app}', '-i', '-e'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
            ans = self._read()
            assert ans == 'hello', 'answer is incorrect, expected="hello", get="{}"'.format(ans)
        except Exception as e:
            raise Exception('{}.{}() {}: {}'.format(
                self.__class__.__name__, currentframe().f_code.co_name, e.__class__.__name__, e))

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
                assert final_ans['num'] == tmp['num'], 'num is incorrect, expected="{}", get="{}"'\
                    .format(final_ans['num'], tmp['num'])
                final_ans = tmp
            return final_ans
        except Exception as e:
            if command.endswith('"app.abort"') and str(e).endswith('\'receiving data on socket failed, error 10054\''):
                return {'status': 'ok'}
            else:
                raise Exception('{}.{}({}) {}: {}'.format(
                    self.__class__.__name__, currentframe().f_code.co_name, command, e.__class__.__name__, e))

    def _read(self):
        ans = self._process.stdout.readline().decode()
        assert ans is not None, 'answer is empty'
        self._log('read: {}'.format(ans))
        final_ans = unquote(ans)
        final_ans = final_ans.rstrip()
        self._log('ans: {}'.format(final_ans))
        return final_ans

    def _write(self, command):
        self._log('write: {}'.format(bytes(command + linesep, encoding='utf-8')))
        self._process.stdin.write(bytes(command + linesep, encoding='utf-8'))
        self._process.stdin.flush()

    def _parse_ans(self, ans):
        assert ans.startswith('ok'), ans
        final_ans = {'status': ans.split(sep='\n', maxsplit=1)[0]}
        if len(ans.split(sep='\n', maxsplit=1)) == 1:
            final_ans['value'] = final_ans['status']
        else:
            if ans.split(sep='\n', maxsplit=1)[1].startswith('post')\
                    or ans.split(sep='\n', maxsplit=1)[1].startswith('send'):
                if ans.split(sep='\n', maxsplit=1)[1].startswith('post'):
                    final_ans['num'] = ans.split(sep='\n', maxsplit=1)[1].split(sep=' ', maxsplit=1)[0][4:]
                if len(ans.split(sep='\n', maxsplit=1)[1].split(sep=' ', maxsplit=1)) == 2:
                    final_ans['value'] = ans.split(sep='\n', maxsplit=1)[1].split(sep=' ', maxsplit=1)[1]
            else:
                final_ans['value'] = ans.split(sep='\n', maxsplit=1)[1]
        self._log('parsed ans: {}'.format(final_ans))
        return final_ans

    def _set_logger(self, logger):
        try:
            assert isinstance(logger, Logger), \
                'argument:logger is incorrect, expected="{}", get="{}"' \
                .format(Logger, type(logger))
            self._logger = logger
        except Exception as e:
            raise Exception('{}.{}() {}: {}'.format(
                self.__class__.__name__, currentframe().f_code.co_name, e.__class__.__name__, e))

    def _log(self, text):
        if self._logger is not None:
            self._logger.log('{} - {}'.format(self.__class__.__name__, text), text_level='DEBUG')

    def __del__(self):
        try:
            self._logger = None
            self._write('quit')
            ans = self._read()
            assert ans == 'bye', 'answer is incorrect, expected="bye", get="{}"'.format(ans)
        except Exception as e:
            raise Exception('{}.{}() {}: {}'.format(
                self.__class__.__name__, currentframe().f_code.co_name, e.__class__.__name__, e))
        finally:
            self._process.stdin.close()
            self._process.terminate()
            self._process.wait(timeout=3)
