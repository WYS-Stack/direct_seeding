import logging
import os
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
# =============== config ===============
LOGGER_NAME = 'dispose'
CONSOLE_LEVEL = logging.INFO
LOG_PATH = Path(os.path.join(dir_path, 'logs'))
# ======================================


INFO_PATH = LOG_PATH / Path('info')
WARNING_PATH = LOG_PATH / Path('warning')
ERROR_PATH = LOG_PATH / Path('error')

INFO_PATH.mkdir(parents=True, exist_ok=True)
WARNING_PATH.mkdir(parents=True, exist_ok=True)
ERROR_PATH.mkdir(parents=True, exist_ok=True)

# create logger
logger = logging.getLogger(LOGGER_NAME)
logger.setLevel(logging.INFO)

# create console handler and set level to info
stream_handler = logging.StreamHandler()
stream_handler.setLevel(CONSOLE_LEVEL)

# create file handler and set level to info
file_name = LOG_PATH.joinpath('info/info.log')
info_handler = TimedRotatingFileHandler(filename=file_name, when='midnight', backupCount=10)
info_handler.setLevel(logging.INFO)

# create file handler and set level to warning
file_name = LOG_PATH.joinpath('warning/warning.log')
warning_handler = TimedRotatingFileHandler(filename=file_name, when='midnight', backupCount=10)
warning_handler.setLevel(logging.WARNING)

# create file handler and set level to error
file_name = LOG_PATH.joinpath('error/error.log')
error_handler = TimedRotatingFileHandler(filename=file_name, when='midnight', backupCount=10)
error_handler.setLevel(logging.ERROR)

# create formatter
stream_formatter = logging.Formatter('[{asctime}][{levelname}] {message}', style='{', datefmt='%Y-%m-%d %H:%M')
file_formatter = logging.Formatter('[{asctime}][{levelname}][1line{lineno}] {message}', style='{', datefmt='%Y-%m-%d %H:%M:%S')

# add formatter to ch
stream_handler.setFormatter(stream_formatter)
info_handler.setFormatter(file_formatter)
warning_handler.setFormatter(file_formatter)
error_handler.setFormatter(file_formatter)

# add ch to logger
logger.addHandler(stream_handler)
logger.addHandler(info_handler)
logger.addHandler(warning_handler)
logger.addHandler(error_handler)

logger.debug('Log module loaded successfully.')

# 'application' code
# logger.debug('debug message')
# logger.info('info message')
# logger.warning('warn message')
# logger.error('error message')
# logger.critical('critical message')
