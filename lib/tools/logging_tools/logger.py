import inspect
import logging
import sys
from platform import system

if "win" in system().lower():
    from ctypes import windll
    console = windll.kernel32
    console.SetConsoleMode(console.GetStdHandle(-11), 7)


VERBOSE = 'VERBOSE'
DEBUG = 'DEBUG'
INFO = 'INFO'
WARNING = 'WARNING'
ERROR = 'ERROR'
CRITICAL = 'CRITICAL'


class Formatter(logging.Formatter):
    _params = {
        VERBOSE:
            {
                'log_timestamp': True,
                'log_levelname': True,
                'log_name': True,
                'background_color': 'black',
                'foreground_color': 'light black'
            },
        DEBUG:
            {
                'log_timestamp': True,
                'log_levelname': True,
                'log_name': True,
                'background_color': 'black',
                'foreground_color': 'white'
            },
        INFO:
            {
                'log_timestamp': True,
                'log_levelname': True,
                'log_name': True,
                'background_color': 'black',
                'foreground_color': 'light white'
            },
        WARNING:
            {
                'log_timestamp': True,
                'log_levelname': True,
                'log_name': True,
                'background_color': 'black',
                'foreground_color': 'light yellow'
            },
        ERROR:
            {
                'log_timestamp': True,
                'log_levelname': True,
                'log_name': True,
                'background_color': 'black',
                'foreground_color': 'light red'
            },
        CRITICAL:
            {
                'log_timestamp': True,
                'log_levelname': True,
                'log_name': True,
                'background_color': 'red',
                'foreground_color': 'light white'
            }
    }

    _fmts = {
        VERBOSE: '',
        DEBUG: '',
        INFO: '',
        WARNING: '',
        ERROR: '',
        CRITICAL: ''
    }

    def __init__(self):
        self._fmts['VERBOSE'] = self._get_formatter('VERBOSE')
        super().__init__(fmt='%(msg)s', datefmt='%Y.%m.%d %H:%M:%S', style='%')

    def format(self, record):

        _original_fmt = self._style._fmt

        if record.levelno == logging.VERBOSE:
            self._style._fmt = self._fmts[VERBOSE]
        elif record.levelno == logging.DEBUG:
            self._style._fmt = self._fmts[DEBUG]
        elif record.levelno == logging.INFO:
            self._style._fmt = self._fmts[INFO]
        elif record.levelno == logging.WARNING:
            self._style._fmt = self._fmts[WARNING]
        elif record.levelno == logging.ERROR:
            self._style._fmt = self._fmts[ERROR]
        elif record.levelno == logging.CRITICAL:
            self._style._fmt = self._fmts[CRITICAL]
        else:
            self._style._fmt = _original_fmt

        return logging.Formatter.format(self, record)

    def _get_formatter(self, level, **new_params):
        tmp = dict()
        tmp.update(self._params[level])
        for param in tmp:
            if param in new_params:
                tmp[param] = new_params[param]

        formatter = ''

        if tmp['log_timestamp']:
            formatter += '%(asctime)s.%(msecs)03d'
        if tmp['log_levelname']:
            formatter += ' - %(levelname)-8s'
        if tmp['log_name']:
            formatter += ' - %(name)s'

        if formatter == '':
            formatter += '%(msg)s'
        else:
            formatter += ' - %(msg)s'

        if tmp['foreground_color'] is not None:
            formatter = self._get_foreground_color(tmp['foreground_color']) + formatter
        if tmp['background_color'] is not None:
            formatter = self._get_background_color(tmp['background_color']) + formatter
        if tmp['foreground_color'] is not None or tmp['background_color'] is not None:
            formatter += self._get_foreground_color('reset')

        return formatter

    def _get_foreground_color(self, color):
        foreground_colors = {
            'reset': '\x1b[0m',
            'black': '\x1b[30m',
            'light black': '\x1b[90m',
            'red': '\x1b[31m',
            'light red': '\x1b[91m',
            'green': '\x1b[32m',
            'light green': '\x1b[92m',
            'yellow': '\x1b[33m',
            'light yellow': '\x1b[93m',
            'blue': '\x1b[34m',
            'light blue': '\x1b[94m',
            'magenta': '\x1b[35m',
            'light magenta': '\x1b[95m',
            'cyan': '\x1b[36m',
            'light cyan': '\x1b[96m',
            'white': '\x1b[37m',
            'light white': '\x1b[97m'
        }
        return foreground_colors[color]

    def _get_background_color(self, color):
        background_colors = {
            'reset': '\x1b[0m',
            'black': '\x1b[40m',
            'light black': '\x1b[100m',
            'red': '\x1b[41m',
            'light red': '\x1b[101m',
            'green': '\x1b[42m',
            'light green': '\x1b[102m',
            'yellow': '\x1b[43m',
            'light yellow': '\x1b[103m',
            'blue': '\x1b[44m',
            'light blue': '\x1b[104m',
            'magenta': '\x1b[45m',
            'light magenta': '\x1b[105m',
            'cyan': '\x1b[46m',
            'light cyan': '\x1b[106m',
            'white': '\x1b[47m',
            'light white': '\x1b[107m'
        }
        return background_colors[color]


class Logger:

    def __init__(self, name, level='INFO'):
        self._set_root_logger()
        self.level = level
        self._logger = logging.getLogger(name)

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, value):
        self._root.setLevel(logging.getLevelName(value))

    def _set_root_logger(self):
        self._root = logging.getLogger()
        logging.VERBOSE = 5
        logging.addLevelName(logging.VERBOSE, VERBOSE)
        logging.Logger.verbose = lambda inst, msg, *args, **kwargs: inst.log(logging.VERBOSE, msg, *args, **kwargs)
        logging.verbose = lambda msg, *args, **kwargs: logging.log(logging.VERBOSE, msg, *args, **kwargs)

        self._fmt = Formatter()
        self._sh = logging.StreamHandler(sys.stdout)
        self._sh.setFormatter(self._fmt)
        self._root.addHandler(self._sh)

    def _log(self, level, msg, **new_params):
        try:
            base_fmt = self._fmt._fmts[level]
            self._fmt._fmts[level] = self._fmt._get_formatter(level, **new_params)
            if level == VERBOSE:
                self._logger.verbose(msg)
            elif level == DEBUG:
                self._logger.debug(msg)
            elif level == INFO:
                self._logger.info(msg)
            elif level == WARNING:
                self._logger.warning(msg)
            elif level == ERROR:
                self._logger.error(msg)
            elif level == CRITICAL:
                self._logger.critical(msg)
            else:
                pass
            self._fmt._fmts[level] = base_fmt
        except Exception as e:
            raise Exception('{}.{}() {}: {}'.format(
                self.__class__.__name__, inspect.currentframe().f_code.co_name, e.__class__.__name__, e))

    def verbose(self, msg: str,
                log_timestamp: bool = None,
                log_levelname: bool = None,
                log_name: bool = None,
                background_color: str = None,
                foreground_color: str = None) -> None:
        arguments = locals()
        new_params = dict()
        for key in arguments.keys():
            if key == 'self' or key == 'myframe' or key == 'msg':
                continue
            if arguments[key] is not None:
                new_params.update({key: arguments[key]})
        self._log(level=VERBOSE, msg=msg, **new_params)

    def debug(self, msg: str,
              log_timestamp: bool = None,
              log_levelname: bool = None,
              log_name: bool = None,
              background_color: str = None,
              foreground_color: str = None) -> None:
        arguments = locals()
        new_params = dict()
        for key in arguments.keys():
            if key == 'self' or key == 'myframe' or key == 'msg':
                continue
            if arguments[key] is not None:
                new_params.update({key: arguments[key]})
        self._log(level=DEBUG, msg=msg, **new_params)

    def info(self, msg: str,
             log_timestamp: bool = None,
             log_levelname: bool = None,
             log_name: bool = None,
             background_color: str = None,
             foreground_color: str = None) -> None:
        arguments = locals()
        new_params = dict()
        for key in arguments.keys():
            if key == 'self' or key == 'myframe' or key == 'msg':
                continue
            if arguments[key] is not None:
                new_params.update({key: arguments[key]})
        self._log(level=INFO, msg=msg, **new_params)

    def warning(self, msg: str,
             log_timestamp: bool = None,
             log_levelname: bool = None,
             log_name: bool = None,
             background_color: str = None,
             foreground_color: str = None) -> None:
        arguments = locals()
        new_params = dict()
        for key in arguments.keys():
            if key == 'self' or key == 'myframe' or key == 'msg':
                continue
            if arguments[key] is not None:
                new_params.update({key: arguments[key]})
        self._log(level=WARNING, msg=msg, **new_params)

    def error(self, msg: str,
             log_timestamp: bool = None,
             log_levelname: bool = None,
             log_name: bool = None,
             background_color: str = None,
             foreground_color: str = None) -> None:
        arguments = locals()
        new_params = dict()
        for key in arguments.keys():
            if key == 'self' or key == 'myframe' or key == 'msg':
                continue
            if arguments[key] is not None:
                new_params.update({key: arguments[key]})
        self._log(level=ERROR, msg=msg, **new_params)

    def critical(self, msg: str,
             log_timestamp: bool = None,
             log_levelname: bool = None,
             log_name: bool = None,
             background_color: str = None,
             foreground_color: str = None) -> None:
        arguments = locals()
        new_params = dict()
        for key in arguments.keys():
            if key == 'self' or key == 'myframe' or key == 'msg':
                continue
            if arguments[key] is not None:
                new_params.update({key: arguments[key]})
        self._log(level=CRITICAL, msg=msg, **new_params)
