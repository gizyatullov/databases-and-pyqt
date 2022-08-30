"""Unit-тесты сервера"""

import unittest
import sys
import os
from time import time

sys.path.append(os.path.join(os.getcwd(), '..'))

from common.variables import *
from server import Server


class TestServer(unittest.TestCase):
    def setUp(self) -> None:
        self.server = Server()
        self.client_message = {
            ACTION: PRESENCE,
            TIME: time(),
            USER: {
                ACCOUNT_NAME: ANON_ACCOUNT_NAME,
            },
        }

        self.server_message_bad_request = {
            RESPONDEFAULT_IP_ADDRESSSE: STATUS_BAD_REQUEST,
            ERROR: 'Bad Request',
        }

    def tearDown(self) -> None:
        pass

    def test_process_client_message(self) -> None:
        response = self.server.process_client_message(message=self.client_message)
        self.assertEqual(response, {RESPONSE: 200})

    def test_process_client_message_error(self) -> None:
        response = self.server.process_client_message(message={})
        self.assertEqual(response, self.server_message_bad_request)

    def test_process_client_message_wrong_action(self) -> None:
        self.client_message[ACTION] = 'param'
        response = self.server.process_client_message(message=self.client_message)
        self.assertEqual(response, self.server_message_bad_request)

    def test_process_client_message_no_action(self) -> None:
        del self.client_message[ACTION]
        response = self.server.process_client_message(message=self.client_message)
        self.assertEqual(response, self.server_message_bad_request)

    def test_process_client_message_no_time(self) -> None:
        del self.client_message[TIME]
        response = self.server.process_client_message(message=self.client_message)
        self.assertEqual(response, self.server_message_bad_request)

    def test_process_client_message_unknown_user(self) -> None:
        self.client_message[USER] = {ACCOUNT_NAME: 'param', }
        response = self.server.process_client_message(message=self.client_message)
        self.assertEqual(response, self.server_message_bad_request)

    def test_process_client_message_no_user(self) -> None:
        del self.client_message[USER]
        response = self.server.process_client_message(message=self.client_message)
        self.assertEqual(response, self.server_message_bad_request)


if __name__ == '__main__':
    unittest.main()
