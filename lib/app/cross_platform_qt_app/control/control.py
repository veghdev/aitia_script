from inspect import currentframe

from cterm import CtermInterface
from tools.class_tools.class_variables import is_class_variables_defined


class Control:

    __cterm_interface = None
    __ip = None
    __port = None
    __app = None
    __path = None

    __pid = None

    def __init__(self, cterm_interface=None, ip=None, port=None, app=None, path=None):
        try:
            if cterm_interface is not None:
                self._set_cterm_interface(cterm_interface)
            if ip is not None:
                self._set_ip(ip)
            if port is not None:
                self._set_port(port)
            if app is not None:
                self._set_app(app)
            if path is not None:
                self._set_path(path)
        except Exception as e:
            raise Exception('{}.{}() {}: {}'.format(
                self.__class__.__name__, currentframe().f_code.co_name, e.__class__.__name__, e))

    def _set_cterm_interface(self, cterm_interface):
        try:
            assert isinstance(cterm_interface, CtermInterface), \
                'argument:cterm_interface is incorrect, expected="{}", get="{}"' \
                .format(CtermInterface, type(cterm_interface))
            self.__cterm_interface = cterm_interface
        except Exception as e:
            raise Exception('{}.{}() {}: {}'.format(
                self.__class__.__name__, currentframe().f_code.co_name, e.__class__.__name__, e))

    def _set_ip(self, ip):
        self.__ip = ip

    def _set_port(self, port):
        self.__port = port

    def _set_app(self, app):
        self.__app = app

    def _set_path(self, path):
        self.__path = path

    def is_available(self):
        try:
            is_class_variables_defined(self, '__cterm_interface', '__ip', '__port')
            ans = self.__cterm_interface.command('send', f'{self.__ip}:{self.__port}', 'app.name')
            # print(ans) # todo logging
            return True
        except Exception as e:
            if str(e).endswith('AssertionError: error \'socket opening error\''):
                return False
            else:
                raise Exception('{}.{}() {}: {}'.format(
                    self.__class__.__name__, currentframe().f_code.co_name, e.__class__.__name__, e))

    def start(self):
        try:
            is_class_variables_defined(self, '__cterm_interface', '__ip', '__port', '__app', '__path')
            self.__pid = self.__cterm_interface.command('pcreate', f'{self.__path}/{self.__app}', '-t', self.__port)
        except Exception as e:
            raise Exception('{}.{}() {}: {}'.format(
                self.__class__.__name__, currentframe().f_code.co_name, e.__class__.__name__, e))

    def stop(self):
        try:
            is_class_variables_defined(self, '__cterm_interface', '__ip', '__port')
            self.__cterm_interface.command('send', f'{self.__ip}:{self.__port}', 'app.abort')
        except Exception as e:
            raise Exception('{}.{}() {}: {}'.format(
                self.__class__.__name__, currentframe().f_code.co_name, e.__class__.__name__, e))

    def open_connection(self, direction, uri):
        try:
            is_class_variables_defined(self, '__cterm_interface', '__ip', '__port')
            self.__cterm_interface.command('send', f'{self.__ip}:{self.__port}', 'connections.open', direction, uri)
        except Exception as e:
            raise Exception('{}.{}() {}: {}'.format(
                self.__class__.__name__, currentframe().f_code.co_name, e.__class__.__name__, e))

    def close_connection(self, direction, connection):
        try:
            is_class_variables_defined(self, '__cterm_interface', '__ip', '__port')
            self.__cterm_interface.command('send', f'{self.__ip}:{self.__port}', 'connections.close', direction, connection)
        except Exception as e:
            raise Exception('{}.{}() {}: {}'.format(
                self.__class__.__name__, currentframe().f_code.co_name, e.__class__.__name__, e))

    def start_proc(self):
        try:
            is_class_variables_defined(self, '__cterm_interface', '__ip', '__port')
            self.__cterm_interface.command('send', f'{self.__ip}:{self.__port}', 'app.startproc')
        except Exception as e:
            raise Exception('{}.{}() {}: {}'.format(
                self.__class__.__name__, currentframe().f_code.co_name, e.__class__.__name__, e))

    def stop_proc(self):
        try:
            is_class_variables_defined(self, '__cterm_interface', '__ip', '__port')
            self.__cterm_interface.command('send', f'{self.__ip}:{self.__port}', 'app.stopproc')
        except Exception as e:
            raise Exception('{}.{}() {}: {}'.format(
                self.__class__.__name__, currentframe().f_code.co_name, e.__class__.__name__, e))

    def stop_proc_sync(self):
        try:
            is_class_variables_defined(self, '__cterm_interface', '__ip', '__port')
            while True:
                ans = self.__cterm_interface.command('send', f'{self.__ip}:{self.__port}', 'app.stopprocsync')
                if ans['value'] == 'ready':
                    break
        except Exception as e:
            raise Exception('{}.{}() {}: {}'.format(
                self.__class__.__name__, currentframe().f_code.co_name, e.__class__.__name__, e))

    def state_clear(self):
        try:
            is_class_variables_defined(self, '__cterm_interface', '__ip', '__port')
            self.__cterm_interface.command('send', f'{self.__ip}:{self.__port}', 'state.clear')
        except Exception as e:
            raise Exception('{}.{}() {}: {}'.format(
                self.__class__.__name__, currentframe().f_code.co_name, e.__class__.__name__, e))

    def state_flush(self):
        try:
            is_class_variables_defined(self, '__cterm_interface', '__ip', '__port')
            self.__cterm_interface.command('send', f'{self.__ip}:{self.__port}', 'state.flush')
        except Exception as e:
            raise Exception('{}.{}() {}: {}'.format(
                self.__class__.__name__, currentframe().f_code.co_name, e.__class__.__name__, e))

    def counters_clear(self):
        try:
            is_class_variables_defined(self, '__cterm_interface', '__ip', '__port')
            self.__cterm_interface.command('send', f'{self.__ip}:{self.__port}', 'counters.clear')
        except Exception as e:
            raise Exception('{}.{}() {}: {}'.format(
                self.__class__.__name__, currentframe().f_code.co_name, e.__class__.__name__, e))
