import pathlib

from inspect import currentframe
import time

from cterm import CtermInterface
from tools.checking_tools.class_checking_tools import is_class_attributes_defined


class Control:
    _cterm_interface = None
    _ip = None
    _port = None
    _app = None

    _pid = None

    def __init__(self, cterm_interface=None, ip=None, port=None, app=None):
        try:
            if cterm_interface is not None:
                self._set_cterm_interface(cterm_interface)
            if ip is not None:
                self._set_ip(ip)
            if port is not None:
                self._set_port(port)
            if app is not None:
                self._set_app(app)
        except Exception as e:
            raise Exception('{}.{}() {}: {}'.format(
                self.__class__.__name__, currentframe().f_code.co_name, e.__class__.__name__, e))

    def _set_cterm_interface(self, cterm_interface):
        try:
            assert isinstance(cterm_interface, CtermInterface), \
                'argument:cterm_interface is incorrect, expected="{}", get="{}"' \
                    .format(CtermInterface, type(cterm_interface))
            self._cterm_interface = cterm_interface
        except Exception as e:
            raise Exception('{}.{}() {}: {}'.format(
                self.__class__.__name__, currentframe().f_code.co_name, e.__class__.__name__, e))

    def _set_ip(self, ip):
        self._ip = ip

    def _set_port(self, port):
        self._port = port

    def _set_app(self, app):
        self._app = pathlib.Path(app)

    def is_available(self):
        try:
            is_class_attributes_defined(self, '_cterm_interface', '_ip', '_port')
            ans = self._cterm_interface.command('send', f'{self._ip}:{self._port}', 'app.name')
            # print(ans) # todo logging
            return True
        except Exception as e:
            if str(e).endswith('AssertionError: error \'socket opening error\''):
                return False
            else:
                raise Exception('{}.{}() {}: {}'.format(
                    self.__class__.__name__, currentframe().f_code.co_name, e.__class__.__name__, e))

    def is_running(self):
        try:
            if self._pid is not None:
                return True
            else:
                return False
        except Exception as e:
            raise Exception('{}.{}() {}: {}'.format(
                self.__class__.__name__, currentframe().f_code.co_name, e.__class__.__name__, e))

    def start(self):
        try:
            is_class_attributes_defined(self, '_cterm_interface', '_ip', '_port', '_app')
            ans = self._cterm_interface.command('pcreate', f'{self._app}', '-t', self._port)
            self._pid = ans['value']
            timeout = time.time() + 60
            while True:
                try:
                    self._cterm_interface.command('send', f'{self._ip}:{self._port}', 'app.name')
                except Exception as e:
                    if time.time() > timeout:
                        raise Exception('{}.{}() {}: {}'.format(
                            self.__class__.__name__, currentframe().f_code.co_name, e.__class__.__name__, e))
                else:
                    break
            return self._pid
        except Exception as e:
            raise Exception('{}.{}() {}: {}'.format(
                self.__class__.__name__, currentframe().f_code.co_name, e.__class__.__name__, e))

    def stop(self):
        try:
            is_class_attributes_defined(self, '_cterm_interface', '_ip', '_port')
            self._cterm_interface.command('send', f'{self._ip}:{self._port}', 'app.abort')
            try:
                timeout = time.time() + 3
                while True:
                    ans = self._cterm_interface.command('ptestpid', self._pid)
                    if ans['value'] == '0':
                        break
                    if time.time() > timeout:
                        self._cterm_interface.command('pdelpid', self._pid)
                        raise Exception('app({}) is still runnig'.format(self._pid))
            except Exception as e:
                timeout = time.time() + 2
                while True:
                    ans = self._cterm_interface.command('pdelpid', self._pid)
                    if ans['value'] == '0':
                        break
                    if time.time() > timeout:
                        raise Exception(e)
            pid = str(self._pid)
            self._pid = None
            return pid
        except Exception as e:
            raise Exception('{}.{}() {}: {}'.format(
                self.__class__.__name__, currentframe().f_code.co_name, e.__class__.__name__, e))

    def open_connection(self, direction, uri):
        try:
            is_class_attributes_defined(self, '_cterm_interface', '_ip', '_port')
            self._cterm_interface.command('send', f'{self._ip}:{self._port}', 'connections.open', direction, uri)
        except Exception as e:
            raise Exception('{}.{}() {}: {}'.format(
                self.__class__.__name__, currentframe().f_code.co_name, e.__class__.__name__, e))

    def close_connection(self, direction, connection):
        try:
            is_class_attributes_defined(self, '_cterm_interface', '_ip', '_port')
            self._cterm_interface.command('send', f'{self._ip}:{self._port}', 'connections.close', direction,
                                          connection)
        except Exception as e:
            raise Exception('{}.{}() {}: {}'.format(
                self.__class__.__name__, currentframe().f_code.co_name, e.__class__.__name__, e))

    def start_proc(self):
        try:
            is_class_attributes_defined(self, '_cterm_interface', '_ip', '_port')
            self._cterm_interface.command('send', f'{self._ip}:{self._port}', 'app.startproc')
        except Exception as e:
            raise Exception('{}.{}() {}: {}'.format(
                self.__class__.__name__, currentframe().f_code.co_name, e.__class__.__name__, e))

    def stop_proc(self):
        try:
            is_class_attributes_defined(self, '_cterm_interface', '_ip', '_port')
            self._cterm_interface.command('send', f'{self._ip}:{self._port}', 'app.stopproc')
        except Exception as e:
            raise Exception('{}.{}() {}: {}'.format(
                self.__class__.__name__, currentframe().f_code.co_name, e.__class__.__name__, e))

    def stop_proc_sync(self):
        try:
            is_class_attributes_defined(self, '_cterm_interface', '_ip', '_port')
            while True:
                ans = self._cterm_interface.command('send', f'{self._ip}:{self._port}', 'app.stopprocsync')
                if ans['value'] == 'ready':
                    break
        except Exception as e:
            raise Exception('{}.{}() {}: {}'.format(
                self.__class__.__name__, currentframe().f_code.co_name, e.__class__.__name__, e))

    def state_clear(self):
        try:
            is_class_attributes_defined(self, '_cterm_interface', '_ip', '_port')
            self._cterm_interface.command('send', f'{self._ip}:{self._port}', 'state.clear')
        except Exception as e:
            raise Exception('{}.{}() {}: {}'.format(
                self.__class__.__name__, currentframe().f_code.co_name, e.__class__.__name__, e))

    def state_flush(self):
        try:
            is_class_attributes_defined(self, '_cterm_interface', '_ip', '_port')
            self._cterm_interface.command('send', f'{self._ip}:{self._port}', 'state.flush')
        except Exception as e:
            raise Exception('{}.{}() {}: {}'.format(
                self.__class__.__name__, currentframe().f_code.co_name, e.__class__.__name__, e))

    def counters_clear(self):
        try:
            is_class_attributes_defined(self, '_cterm_interface', '_ip', '_port')
            self._cterm_interface.command('send', f'{self._ip}:{self._port}', 'counters.clear')
        except Exception as e:
            raise Exception('{}.{}() {}: {}'.format(
                self.__class__.__name__, currentframe().f_code.co_name, e.__class__.__name__, e))

    def save_config(self):
        try:
            is_class_attributes_defined(self, '_cterm_interface', '_ip', '_port')
            self._cterm_interface.command('send', f'{self._ip}:{self._port}', 'config.save')
        except Exception as e:
            raise Exception('{}.{}() {}: {}'.format(
                self.__class__.__name__, currentframe().f_code.co_name, e.__class__.__name__, e))

    def set_config(self, section, parameter, value):
        try:
            is_class_attributes_defined(self, '_cterm_interface', '_ip', '_port')
            ans = {
                'section': section,
                'parameter': parameter,
                'prev_value': self._cterm_interface.command('send',
                                                            f'{self._ip}:{self._port}',
                                                            'config.get',
                                                            section,
                                                            parameter)['value'].replace('{}/{}='.format(section,
                                                                                                        parameter),
                                                                                        ''),
                'value': value
            }
            self._cterm_interface.command('send', f'{self._ip}:{self._port}', 'config.set', section, parameter, value)
            return ans
        except Exception as e:
            raise Exception('{}.{}() {}: {}'.format(
                self.__class__.__name__, currentframe().f_code.co_name, e.__class__.__name__, e))

    def send_command(self, *command):
        try:
            is_class_attributes_defined(self, '_cterm_interface', '_ip', '_port')
            ans = self._cterm_interface.command('send', f'{self._ip}:{self._port}', *command)
            return ans
        except Exception as e:
            raise Exception('{}.{}() {}: {}'.format(
                self.__class__.__name__, currentframe().f_code.co_name, e.__class__.__name__, e))
