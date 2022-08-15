"""Конфиг клиентского логгера"""

import logging
from pathlib import Path
import sys

sys.path.append(f'{Path(__file__).resolve().parent.parent}')
from common.variables import LOGGING_LEVEL

BASE_DIR = Path(__file__).resolve().parent
PATH_LOG_FILE = Path(BASE_DIR, 'client.log')

FORMATTER = logging.Formatter('%(asctime)s %(levelname)s %(message)s %(filename)s')

FILE_HANDLER = logging.FileHandler(filename=PATH_LOG_FILE, encoding='utf-8')
FILE_HANDLER.setFormatter(FORMATTER)
FILE_HANDLER.setLevel(level=logging.DEBUG)

STREAM_HANDLER = logging.StreamHandler(sys.stdout)
STREAM_HANDLER.setFormatter(FORMATTER)
STREAM_HANDLER.setLevel(level=LOGGING_LEVEL)

CLIENT_LOGGER = logging.getLogger('client_logger')
CLIENT_LOGGER.setLevel(level=logging.DEBUG)
CLIENT_LOGGER.addHandler(FILE_HANDLER)
CLIENT_LOGGER.addHandler(STREAM_HANDLER)

if __name__ == '__main__':
    CLIENT_LOGGER.debug('debug check')
    CLIENT_LOGGER.info('info check')
    CLIENT_LOGGER.warning('warning check')
    CLIENT_LOGGER.error('error check')
    CLIENT_LOGGER.critical('critical check')
