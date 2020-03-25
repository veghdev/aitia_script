import logging
from inspect import currentframe
from platform import system
from datetime import date

if "win" in system().lower():
    from ctypes import windll
    console = windll.kernel32
    console.SetConsoleMode(console.GetStdHandle(-11), 7)


class Logger:

    __logger = None
    __log_level = None
    __log_file = None
    __timestamp = None
    __foreground_color = None
    __background_color = None

    def __init__(self,
                 logger='logger',
                 log_level='INFO',
                 log_file=None,
                 timestamp=True,
                 foreground_color=None,
                 background_color=None):
        try:
            self.set__logger(logger)
            self.set__log_level(log_level)
            self.set__log_file(log_file)
            self.set__timestamp(timestamp)
            self.set__foreground_color(foreground_color)
            self.set__background_color(background_color)

        except Exception as e:
            raise Exception('{}.{}() {}: {}'.format(
                self.__class__.__name__, currentframe().f_code.co_name, e.__class__.__name__, e))

    def set__logger(self, logger):
        self.__logger = logger

    def set__log_level(self, log_level):
        self.__log_level = log_level

    def set__log_file(self, log_file):
        self.__log_file = log_file

    def set__timestamp(self, timestamp):
        self.__timestamp = timestamp

    def set__foreground_color(self, foreground_color):
        self.__foreground_color = foreground_color

    def set__background_color(self, background_color):
        self.__background_color = background_color

    def log(self,
            text,
            text_level='INFO',
            logger='default',
            log_level='default',
            log_file='default',
            timestamp='default',
            foreground_color='default',
            background_color='default'):
        try:
            if logger == 'default':
                logger = self.__logger
            if log_level == 'default':
                log_level = self.__log_level
            if log_file == 'default':
                log_file = self.__log_file
            if timestamp == 'default':
                timestamp = self.__timestamp
            if foreground_color == 'default':
                foreground_color = self.__foreground_color
            if background_color == 'default':
                background_color = self.__background_color

            log = self.__create_logger(logger, log_level, log_file, timestamp, foreground_color, background_color)
            if text_level == 'DEBUG':
                log.debug('   ' + ' - ' + text)
            if text_level == 'INFO':
                log.info('    ' + ' - ' + text)
            if text_level == 'WARNING':
                log.warning(' ' + ' - ' + text)
            if text_level == 'ERROR':
                log.error('   ' + ' - ' + text)
            if text_level == 'CRITICAL':
                log.critical(' - ' + text)
            log.handlers.clear()

        except Exception as e:
            raise Exception('{}.{}() {}: {}'.format(
                self.__class__.__name__, currentframe().f_code.co_name, e.__class__.__name__, e))

    def __create_logger(self, logger, log_level, log_file, timestamp, foreground_color, background_color):
        log = logging.getLogger(logger)
        log.setLevel(logging.getLevelName(log_level))

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(self.__create_formatter(timestamp, foreground_color, background_color))
        log.addHandler(stream_handler)

        if log_file is not None:
            file_name = log_file + date.today().strftime("_%Y%m%d.log")
            file_handler = logging.FileHandler(file_name)
            file_handler.setFormatter(self.__create_formatter(timestamp, None, None))
            log.addHandler(file_handler)

        return log

    def __create_formatter(self, timestamp, foreground_color, background_color):
        formatter = ''
        if foreground_color is not None:
            formatter = formatter + self.__get_foreground_color(foreground_color)
        if background_color is not None:
            formatter = formatter + self.__get_background_color(background_color)
        if timestamp is True:
            formatter = formatter + '%(asctime)s - '
        formatter = formatter + '%(name)s - '
        formatter = formatter + '%(levelname)s'
        formatter = formatter + '%(message)s'
        if foreground_color is not None or background_color is not None:
            formatter = formatter + '\033[;1;0m'
        formatter = logging.Formatter(formatter)
        return formatter

    def __get_foreground_color(self, color):
        colors = {
            'black': '\x1b[30m',
            'light black': '\x1b[90m',
            'red': '\x1b[31m',
            'light red': '\x1b[91m',
            'green': '\x1b[32m',
            'light green': '\x1b[92m',
            'yellow': '\x1b[33m',
            'light yellow': '\x1b93m',
            'blue': '\x1b[34m',
            'light blue': '\x1b[94m',
            'magenta': '\x1b[35m',
            'light magenta': '\x1b[95m',
            'cyan': '\x1b[36m',
            'light cyan': '\x1b[96m',
            'white': '\x1b[37m',
            'light white': '\x1b[97m'
        }
        return colors[color]

    def __get_background_color(self, color):
        colors = {
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
        return colors[color]
