import logging

MIN_PORT_NUMBER = 1024
MAX_PORT_NUMBER = 65535

ANON_ACCOUNT_NAME = 'anonymous'

DEFAULT_LISTEN_ADDRESS = ''
DEFAULT_PORT = 5151
DEFAULT_IP_ADDRESS = '127.0.0.1'
MAX_CONNECTIONS = 1
MAX_PACKAGE_LENGTH = 1024
ENCODING = 'utf-8'

ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'
SENDER = 'from'
EXIT = 'exit'

PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'
MESSAGE = 'message'
MESSAGE_TEXT = 'message_text'
RESPONDEFAULT_IP_ADDRESSSE = 'respondefault_ip_addressse'

STATUS_OK = 200
STATUS_BAD_REQUEST = 400

LOGGING_LEVEL = logging.DEBUG

EXIT_CLIENT_CHAR = '^'

ACCEPTABLE_CLIENT_MODES: tuple = ('listen', 'send')

NAME_IS_OCCUPIED = 'Имя пользователя уже занято.'
REQUEST_IS_INCORRECT = 'Запрос некорректен.'
DESTINATION = 'to'

RESPONSE_200 = {RESPONSE: 200}
RESPONSE_400 = {
    RESPONSE: 400,
    ERROR: None
}
