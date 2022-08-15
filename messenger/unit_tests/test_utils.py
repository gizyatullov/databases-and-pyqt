"""Unit-тесты утилит"""

import unittest
import sys
import json
from time import time
from pathlib import Path

sys.path.append(f'{Path(__file__).resolve().parent.parent}')
from common.variables import *
from common.utils import Utils
from errors import NotDict, NotBytes, MaxLen


class TestSocket:
    def __init__(self, test_data: dict = None, give_away_bytes=True) -> None:
        self.test_data = test_data
        self.encoded_message = ''
        self.received_message = ''
        self.send_encoded_message = ''

        self.give_away_bytes = give_away_bytes

    def send_message(self, message: dict) -> None:
        """Имитация отправления в сокет"""
        self.received_message = message
        json_message = json.dumps(message)
        self.encoded_message = json_message.encode(ENCODING)

    def recv(self, max_len_message: int) -> None:
        """Имитация чтения из сокета"""
        json_message = json.dumps(self.test_data)
        if len(json_message) > max_len_message:
            raise MaxLen
        if self.give_away_bytes:
            return json_message.encode(ENCODING)
        return json_message

    def send(self, message: bytes) -> None:
        decode_message = message.decode(ENCODING)
        json_message = json.loads(decode_message)
        self.send_encoded_message = json_message


class TestUtils(unittest.TestCase):
    def setUp(self) -> None:
        self.utils = Utils()
        self.time = time()
        self.dict_for_send = {
            ACTION: PRESENCE,
            TIME: self.time,
            USER: {
                ACCOUNT_NAME: 'test_user'
            }
        }

        self.test_dict_recv_err = {
            RESPONSE: 400,
            ERROR: 'Bad Request'
        }

    def tearDown(self) -> None:
        pass

    def test_get_message(self) -> None:
        response = self.utils.get_message(TestSocket(self.dict_for_send))
        self.assertEqual(response, self.dict_for_send)

    def test_get_message_no_dict(self) -> None:
        self.assertRaises(NotDict, self.utils.get_message, TestSocket(''))

    def test_get_message_not_bytes(self) -> None:
        self.assertRaises(NotBytes, self.utils.get_message, TestSocket(self.dict_for_send, give_away_bytes=False))

    def test_get_message_len_error(self) -> None:
        self.assertRaises(MaxLen, self.utils.get_message, TestSocket({'param': 'a' * 1024}))

    def test_get_message_bad_request(self) -> None:
        response = self.utils.get_message(TestSocket(self.test_dict_recv_err))
        self.assertEqual(response, self.test_dict_recv_err)

    def test_send_message(self) -> None:
        sock_send = TestSocket()
        response = self.utils.send_message(sock_send, self.dict_for_send)
        self.assertEqual(sock_send.send_encoded_message, self.dict_for_send)

    def test_send_message_not_dict(self) -> None:
        sock_send = TestSocket()
        self.assertRaises(NotDict, self.utils.send_message, sock_send, '')


if __name__ == '__main__':
    unittest.main()
