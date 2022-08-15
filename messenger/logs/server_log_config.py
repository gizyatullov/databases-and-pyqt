"""Конфиг серверного логгера"""

import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
import sys

sys.path.append(f'{Path(__file__).resolve().parent.parent}')
from common.variables import LOGGING_LEVEL

BASE_DIR = Path(__file__).resolve().parent
PATH_LOG_FILE = Path(BASE_DIR, 'server.log')

FORMATTER = logging.Formatter('%(asctime)s %(levelname)s %(message)s %(filename)s')

FILE_HANDLER = TimedRotatingFileHandler(filename=PATH_LOG_FILE, encoding='utf-8', interval=1, when='D')
FILE_HANDLER.setFormatter(FORMATTER)
FILE_HANDLER.setLevel(level=LOGGING_LEVEL)

STREAM_HANDLER = logging.StreamHandler(sys.stdout)
STREAM_HANDLER.setFormatter(FORMATTER)
STREAM_HANDLER.setLevel(level=LOGGING_LEVEL)

SERVER_LOGGER = logging.getLogger('server_logger')
SERVER_LOGGER.setLevel(level=LOGGING_LEVEL)
SERVER_LOGGER.addHandler(FILE_HANDLER)
SERVER_LOGGER.addHandler(STREAM_HANDLER)

if __name__ == '__main__':
    SERVER_LOGGER.debug('debug check')
    SERVER_LOGGER.info('info check')
    SERVER_LOGGER.warning('warning check')
    SERVER_LOGGER.error('error check')
    SERVER_LOGGER.critical('critical check')
