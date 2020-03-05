from subprocess import Popen, PIPE
from urllib.parse import unquote
from os import linesep
from inspect import currentframe


class CtermInterface:

    def __init__(self, cterm):
        try:
            self.process = Popen([cterm, '-i', '-e'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
            ans = self.__read()
            assert ans == 'hello', f'answer is incorrect, expected="hello", get="{ans}"'
        except Exception as e:
            raise Exception(
                f'{ self.__class__.__name__}.{ currentframe().f_code.co_name}() { e.__class__.__name__}: {e}')

    def command(self, command, *params):
        try:
            param = '" "'.join(params)
            if param != '':
                command = command + ' ' + '"' + param + '"'
            self.__write(command)
            ans = self.__read()
            final_ans = self.__parse_ans(ans)
            if command.startswith('post'):
                ans = self.__read()
                tmp = self.__parse_ans(ans)
                assert final_ans['num'] == tmp['num'], 'num is incorrect, expected="{}", get="{}"'\
                    .format(final_ans['num'], tmp['num'])
                final_ans = tmp
            return final_ans
        except Exception as e:
            raise Exception(
                f'{self.__class__.__name__}.{ currentframe().f_code.co_name}({command}) {e.__class__.__name__}: {e}')

    def __read(self):
        ans = self.process.stdout.readline().decode()
        assert ans is not None, 'answer is empty'
        ans = unquote(ans)
        ans = ans.rstrip()
        return ans

    def __write(self, command):
        self.process.stdin.write(bytes(command + linesep, encoding='utf-8'))
        self.process.stdin.flush()

    def __parse_ans(self, ans):
        assert ans.startswith('ok'), ans
        final_ans = {'status': ans.split(sep='\n', maxsplit=1)[0]}
        if ans.split(sep='\n', maxsplit=1)[1].startswith('post')\
                or ans.split(sep='\n', maxsplit=1)[1].startswith('send'):
            final_ans['num'] = ans.split(sep='\n', maxsplit=1)[1].split(sep=' ', maxsplit=1)[0][4:]
            if len(ans.split(sep='\n', maxsplit=1)[1].split(sep=' ', maxsplit=1)) == 2:
                final_ans['value'] = ans.split(sep='\n', maxsplit=1)[1].split(sep=' ', maxsplit=1)[1]
        else:
            final_ans['value'] = ans.split(sep='\n', maxsplit=1)[1]
        return final_ans

    def __del__(self):
        try:
            self.__write('quit')
            ans = self.__read()
            assert ans == 'bye', f'answer is incorrect, expected="bye", get="{ans}"'
        except Exception as e:
            raise Exception(
                f'{self.__class__.__name__}.{currentframe().f_code.co_name}() {e.__class__.__name__}: {e}')
        finally:
            self.process.stdin.close()
            self.process.terminate()
            self.process.wait(timeout=3)





