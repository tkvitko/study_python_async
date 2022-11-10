import unittest

from homework_04.client import send_presence_to_server


class TestClient(unittest.TestCase):
    # Тесты клиента запускаются только при работающем тестовом сервере
    test_server = ('0.0.0.0', 8000)

    def test_send_presence_to_server(self):
        self.assertEqual(send_presence_to_server(*self.test_server), None)


if __name__ == '__main__':
    unittest.main()
