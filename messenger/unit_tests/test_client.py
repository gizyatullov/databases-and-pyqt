"""Unit-тесты клиента"""

import unittest
import sys
import os

sys.path.append(os.path.join(os.getcwd(), '..'))

from common.variables import *
from client import Client


class TestClient(unittest.TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.time = 1653374086.2337894
        self.presence_message = {
            ACTION: PRESENCE,
            TIME: self.time,
            USER: {
                ACCOUNT_NAME: ANON_ACCOUNT_NAME,
            },
        }

        self.server_message_ok = {
            'response': 200,
        }
        self.server_message_error = {
            'response': 400,
            'error': 'Bad Request',
        }

    def tearDown(self) -> None:
        pass

    def test_create_presence(self) -> None:
        response = self.client.create_presence()
        response['time'] = self.time
        self.assertEqual(response, self.presence_message)

    def test_create_presence_error(self) -> None:
        response = self.client.create_presence()
        self.assertNotEqual(response, self.presence_message)

    def test_parse_server_message(self) -> None:
        response = self.client.parse_server_message(message=self.server_message_ok)
        self.assertEqual(response, '200 OK')

    def test_parse_server_message_bad_request(self) -> None:
        response = self.client.parse_server_message(message=self.server_message_error)
        self.assertEqual(response, '400 Bad Request')

    def test_parse_server_message_raise_error(self) -> None:
        self.assertRaises(ValueError, self.client.parse_server_message, message={})


if __name__ == '__main__':
    unittest.main()
