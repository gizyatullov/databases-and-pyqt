"""Декораторы логирования"""

import sys
import logging
import inspect
import traceback
from functools import wraps

sys.path.append('../')
from logs import client_log_config
from logs import server_log_config

name_coll_module = sys.argv[0].split('/')[-1]

match name_coll_module:
    case 'client.py':
        LOGGER = logging.getLogger('client_logger')
    case 'server.py':
        LOGGER = logging.getLogger('server_logger')
    case _:
        raise NameError


def log(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        LOGGER.debug(f'Вызов функции {func.__name__} из модуля {func.__module__} \n'
                     f'с параметрами позиционными {args or "нет"} и именованными {kwargs or "нет"}, \n'
                     f'функцией {inspect.stack()[1][3]} из модуля {name_coll_module}. \n')
        response = func(*args, **kwargs)
        return response

    return wrapper


class Log:
    def __init__(self, comment: str = '«no comments»'):
        self.comment = comment

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            LOGGER.debug(f'Вызов функции {func.__name__} из модуля {func.__module__} \n'
                         f'с параметрами позиционными {args or "нет"} и именованными {kwargs or "нет"}, \n'
                         f'функцией {traceback.format_stack()[0].strip().split()[-1]} из модуля {name_coll_module}. \n'
                         f'С комментарием {self.comment}.\n')
            response = func(*args, **kwargs)
            return response

        return wrapper
