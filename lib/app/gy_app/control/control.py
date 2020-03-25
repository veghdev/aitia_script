from inspect import currentframe

from cterm import CtermInterface
from tools.checking_tools.class_checking_tools import is_class_attributes_defined

from tools.logging_tools.logger import Logger


class Control:
    _cterm_interface = None
    _app = None
    _path = None
    _logger = None

    _pid = None

    def __init__(self, cterm_interface=None, app=None, path=None, logger=None):
        try:
            if logger is not None:
                self._set_logger(logger)
            if cterm_interface is not None:
                self._set_cterm_interface(cterm_interface)
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
            self._cterm_interface = cterm_interface
        except Exception as e:
            raise Exception('{}.{}() {}: {}'.format(
                self.__class__.__name__, currentframe().f_code.co_name, e.__class__.__name__, e))

    def _set_app(self, app):
        self._app = app

    def _set_path(self, path):
        self._path = path

    def start(self):
        try:
            is_class_attributes_defined(self, '_cterm_interface', '_app', '_path')
            ans = self._cterm_interface.command('pcreate', f'{self._path}/{self._app}')
            self._pid = ans['value']
            self._log(f'start app: {self._path}/{self._app}, pid: {self._pid}')
        except Exception as e:
            raise Exception('{}.{}() {}: {}'.format(
                self.__class__.__name__, currentframe().f_code.co_name, e.__class__.__name__, e))

    def stop(self):
        try:
            is_class_attributes_defined(self, '_cterm_interface', '_app', '_pid')
            ans = self._cterm_interface.command('closewindow', self._app)
            while True:
                ans = self._cterm_interface.command('clickbutton', self._pid,
                                                     'Are you sure to quit this software module', 'Yes')
                if ans['value'] == 'done':
                    break
            while True:
                ans = self._cterm_interface.command('clickbutton', self._pid,
                                                     'Ready to quit', 'OK')
                if ans['value'] == 'done':
                    break
        except Exception as e:
            raise Exception('{}.{}() {}: {}'.format(
                self.__class__.__name__, currentframe().f_code.co_name, e.__class__.__name__, e))

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


class ControlSgaCDRQueryServer(Control):
    pass


class ControlSgaAutho(Control):
    def start(self):
        try:
            super().start()
            while True:
                ans = self._cterm_interface.command('clickbutton', self._pid,
                                                     'sCreatePassword', 'OK')
                if ans['value'] == 'done':
                    break
            while True:
                ans = self._cterm_interface.command('clickbutton', self._pid,
                                                     'Warning: sCreatePassword', 'OK')
                if ans['value'] == 'done':
                    break
        except Exception as e:
            raise Exception('{}.{}() {}: {}'.format(
                self.__class__.__name__, currentframe().f_code.co_name, e.__class__.__name__, e))
