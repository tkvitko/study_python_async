import unittest

from cource_project.server import process_message
from .testdata import *


class TestServer(unittest.TestCase):

    def test_process_request_success(self):
        self.assertEqual(process_message(message_good)['response'], 200)

    def test_process_request_without_action(self):
        self.assertEqual(process_message(message_without_action)['response'], 400)

    def test_process_request_with_wrong_action(self):
        self.assertEqual(process_message(message_with_wrong_action)['response'], 400)


if __name__ == '__main__':
    unittest.main()
