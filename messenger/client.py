import argparse
import socket
import json
import sys
from sys import argv, exit
import time
import logging
import threading

from common.utils import Utils
from common.variables import *
import logs.client_log_config
from logs.decorators import log, Log
from metaclasses import ClientVerifier

CLIENT_LOGGER = logging.getLogger('client_logger')


class Client(Utils, ClientVerifier):
    def __init__(self):
        self.server_address: str = DEFAULT_IP_ADDRESS
        self.server_port: int = DEFAULT_PORT
        self.client_mode: str = ''

        self.message: dict = {}
        self.message_from_server = {}

        self.sock = socket.socket()
        self.account_name = None

        self.presence_request: dict = {}

        self.exit_message: dict = {}

    @log
    def create_exit_message(self):
        """Создаёт словарь с сообщением о выходе"""
        self.exit_message = {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: self.account_name
        }

    @log
    def handler_message_from_server(self):
        while True:
            try:
                self.message_from_server = self.get_message(self.sock)
                if (ACTION in self.message_from_server and self.message_from_server[ACTION] == MESSAGE and
                        SENDER in self.message_from_server and
                        DESTINATION in self.message_from_server and
                        MESSAGE_TEXT in self.message_from_server and
                        self.message_from_server[DESTINATION] == self.account_name):
                    CLIENT_LOGGER.info(
                        f'Получено сообщение от пользователя {self.message_from_server[SENDER]}:'
                        f'\n{self.message_from_server[MESSAGE_TEXT]}')
                else:
                    CLIENT_LOGGER.error(f'Получено некорректное сообщение с сервера: {self.message_from_server}')
            except (OSError, ConnectionError, ConnectionAbortedError,
                    ConnectionResetError, json.JSONDecodeError):
                CLIENT_LOGGER.critical(f'Потеряно соединение с сервером.')
                exit(1)

    # @logs
    def create_message(self):
        to_user: str = input('Введите получателя сообщения: ')
        message: str = input(f'Введите сообщение для отправки: ')
        message: dict = {
            ACTION: MESSAGE,
            SENDER: self.account_name,
            DESTINATION: to_user,
            TIME: time.time(),
            MESSAGE_TEXT: message,
        }
        CLIENT_LOGGER.debug(f'Сформирован словарь сообщения: {message}')
        self.message = message
        try:
            self.send_message(self.sock, self.message)
            CLIENT_LOGGER.info(f'Отправлено сообщение для пользователя {to_user}')
        except Exception:
            CLIENT_LOGGER.critical('Потеряно соединение с сервером.')
            exit(1)

    # @logs
    def user_interactive(self):
        """Взаимодействие с пользователем, запрашивает команды, отправляет сообщения"""
        self.print_help()
        while True:
            command = input('Введите команду: ')
            match command:
                case 'message':
                    self.create_message()
                case 'help':
                    self.print_help()
                case 'exit':
                    self.create_exit_message()
                    self.send_message(self.sock, self.exit_message)
                    CLIENT_LOGGER.info('Завершение соединения.')
                    CLIENT_LOGGER.info('Завершение работы по команде пользователя.')
                    # Задержка необходима, чтобы успело уйти сообщение о выходе
                    time.sleep(0.5)
                    break
                case _:
                    sys.stdout.write('Команда не распознана, попробуйте снова. help - вывести поддерживаемые команды.')

    # @logs
    def create_presence(self) -> None:
        """Генерирует запрос о присутствии клиента"""
        out = {
            ACTION: PRESENCE,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: self.account_name,
            },
        }
        CLIENT_LOGGER.debug(f'Сформировано {PRESENCE} сообщение для пользователя {out.get(USER).get(ACCOUNT_NAME)}')
        self.presence_request = out

    # @logs
    def print_help(self):
        """Выводит справку по использованию."""
        sys.stdout.write(f'Поддерживаемые команды:\n'
                         f'message - отправить сообщение. Кому и текст будет запрошены отдельно.\n'
                         f'help - вывести подсказки по командам\n'
                         f'exit - выход из программы\n'
                         f'Я КЛИЕНТ')

    # @logs
    def parse_server_message(self) -> str:
        """Разбирает ответ сервера на сообщение о присутствии,
        возвращает 200 если все ОК или генерирует исключение при ошибке"""
        # CLIENT_LOGGER.debug(f'Разбор приветственного сообщения от сервера: {message}')
        if RESPONSE in self.message_from_server:
            if self.message_from_server[RESPONSE] == STATUS_OK:
                return f'{STATUS_OK} OK'
            raise ValueError(f'{STATUS_BAD_REQUEST} : {self.message_from_server[ERROR]}')
        raise ValueError(RESPONSE)

    # @logs
    def check_port(self) -> None:
        if self.server_port < MIN_PORT_NUMBER or self.server_port > MAX_PORT_NUMBER:
            CLIENT_LOGGER.critical(
                f'Попытка запуска клиента с указанием неподходящего порта {self.server_port}. Допустимы адреса с {MIN_PORT_NUMBER} до {MAX_PORT_NUMBER}.')
            exit(1)

    # @logs
    def check_mode(self):
        if self.client_mode not in ACCEPTABLE_CLIENT_MODES:
            CLIENT_LOGGER.critical(
                f'Указан недопустимый режим работы {self.client_mode}, допустимые режимы: {ACCEPTABLE_CLIENT_MODES}')
            exit(1)

    # @logs
    def arguments_parser(self) -> None:
        parser = argparse.ArgumentParser()
        parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
        parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
        parser.add_argument('-n', '--name', default=None, nargs='?')
        name_space = parser.parse_args(sys.argv[1:])
        self.server_address = name_space.addr
        self.server_port = name_space.port
        self.account_name = name_space.name
        self.check_port()

    # @logs
    def set_user_name(self):
        self.account_name = input('Введите имя пользователя: ')

    @Log()
    def main(self):
        self.arguments_parser()
        CLIENT_LOGGER.info(
            f'Запущен клиент с параметрами, адрес сервера: {self.server_address}, порт: {self.server_port}.')

        if not self.account_name:
            while self.account_name is None:
                self.set_user_name()
        sys.stdout.write(f'Консольный мессенджер. Клиентский модуль. Имя пользователя: {self.account_name}')

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.server_address, self.server_port))
            self.create_presence()
            self.send_message(self.sock, self.presence_request)
            self.message_from_server = self.get_message(self.sock)
            answer = self.parse_server_message()
            CLIENT_LOGGER.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
        except json.JSONDecodeError:
            CLIENT_LOGGER.error('Не удалось декодировать полученную Json строку.')
            input()
            exit(1)
        except Exception:
            CLIENT_LOGGER.error('Неизвестная ошибка.')
            exit(1)
        else:
            receiver = threading.Thread(target=self.handler_message_from_server, daemon=True)
            receiver.start()

            user_interface = threading.Thread(target=self.user_interactive, daemon=True)
            user_interface.start()

            CLIENT_LOGGER.debug('Запущены процессы')

            while True:
                time.sleep(1)
                if receiver.is_alive() and user_interface.is_alive():
                    continue
                break


if __name__ == '__main__':
    client = Client()
    try:
        client.main()
    except KeyboardInterrupt:
        pass
