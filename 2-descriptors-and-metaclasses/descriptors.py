import logging

from common.variables import MIN_PORT_NUMBER, MAX_PORT_NUMBER, DEFAULT_PORT

server_logger = logging.getLogger('server_logger')


class PortDesc:
    def __set_name__(self, owner, title_attr):
        self.title_attr = title_attr

    def __set__(self, instance, value=DEFAULT_PORT):
        try:
            value = int(value)
        except ValueError('Значение должно быть целым числом!'):
            pass

        if not MIN_PORT_NUMBER < value < MAX_PORT_NUMBER:
            mess = f'Значение не может быть меньше {MIN_PORT_NUMBER} и больше {MAX_PORT_NUMBER}! У Вас {value}!'
            server_logger.critical(mess)
            raise ValueError(mess)

        instance.__dict__[self.title_attr] = value

    def __get__(self, instance, owner):
        return instance.__dict__[self.title_attr]
