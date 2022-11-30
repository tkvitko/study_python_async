import sys
import json
import socket
import time
import argparse
import logging
import threading
import chat.client_log_config
from chat.constants import DEFAULT_PORT, DEFAULT_IP
from chat.functions import receive_message, send_message, log
from chat.metaclasses import ClientVerifier

LOGGER = logging.getLogger('client')


class ServerError(Exception):
    """Исключение - ошибка сервера"""

    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text


class Client(metaclass=ClientVerifier):

    # @log
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--addr', '-a', help="ip address to listen on", type=str, default=DEFAULT_IP)
        parser.add_argument('--port', '-p', help="tcp port to listen on", type=int, default=DEFAULT_PORT)
        parser.add_argument('--name', '-n', help="user name", type=str, default=None)
        args = parser.parse_args()
        self.server_addr = args.addr
        self.server_port = args.port
        self.username = args.name

    # @log
    @staticmethod
    def receive_message_from_server(sock, me):
        while True:
            try:
                message = receive_message(sock)
                if 'action' in message and message['action'] == 'message' and 'from' in message and 'to' in message \
                        and 'message_text' in message and message['to'] == me:
                    print(f'\nMessage received from {message["from"]}: \n{message["message_text"]}')
                    LOGGER.info(f'\nMessage received from {message["from"]}: \n{message["message_text"]}')
                else:
                    LOGGER.error(f'Wrong message received from server: {message}')
            except (OSError, ConnectionError, ConnectionAbortedError,
                    ConnectionResetError, json.JSONDecodeError):
                LOGGER.critical(f'Connection with server lost')
                break

    # @log
    @staticmethod
    def create_message(sock, account_name):
        message_dict = {
            'action': 'message',
            'from': account_name,
            'to': input('To: '),
            'time': time.time(),
            'message_text': input('Text: ')
        }
        LOGGER.debug(f'Dict message here: {message_dict}')
        try:
            send_message(sock, message_dict)
            LOGGER.info(f'Message sent to {message_dict["to"]}')
        except:
            LOGGER.critical('Connection with server lost')
            sys.exit(1)

    # @log
    def user_interactions(self, sock, username):
        self.print_help()
        while True:
            command = input('Enter command here: ')
            if command == 'message':
                self.create_message(sock, username)
            elif command == 'help':
                self.print_help()
            elif command == 'exit':
                exit_message = {
                    'action': 'exit',
                    'time': time.time(),
                    'account_name': username
                }
                send_message(sock, exit_message)
                print('Connection closed')
                LOGGER.info('Connection closed by user')
                time.sleep(0.5)
                break
            else:
                print('Bad command or filename. Type help')

    # @log
    @staticmethod
    def create_presence(account_name):
        """Функция генерирует запрос о присутствии клиента"""
        presence_body = {
            'action': 'presence',
            'time': time.time(),
            'user': {
                'account_name': account_name
            }
        }
        LOGGER.debug(f'Presence has been created for {account_name}')
        return presence_body

    @staticmethod
    def print_help():
        print('Commands list:')
        print('message - send message to user')
        print('help - this help')
        print('exit - close client')

    # @log
    @staticmethod
    def process_response_ans(message):
        LOGGER.debug(f'Разбор приветственного сообщения от сервера: {message}')
        if 'response' in message:
            if message['response'] == 200:
                return '200 : OK'
            elif message['response'] == 400:
                raise ServerError(f'400 : {message["error"]}')

    def start(self):
        print('Client started')

        # Если имя пользователя не было задано, необходимо запросить пользователя.
        if not self.username:
            self.username = input('Enter your name: ')

        LOGGER.info(
            f'Client started: server is {self.server_addr}:{self.server_port}, username is: {self.username}')

        try:
            transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            transport.connect((self.server_addr, self.server_port))
            presence_message = self.create_presence(self.username)
            send_message(transport, presence_message)
            answer = self.process_response_ans(receive_message(transport))
            LOGGER.info(f'Connected to server. Server answer: {answer}')
            print(f'Connected to server. Server answer: {answer}')
        except json.JSONDecodeError:
            LOGGER.error('Problems with JSON from server')
            sys.exit(1)
        except ServerError as error:
            LOGGER.error(f'Error from server: {error.text}')
            sys.exit(1)
        except (ConnectionRefusedError, ConnectionError):
            LOGGER.critical(
                f'Cant connect to server {self.server_addr}:{self.server_port}')
            sys.exit(1)
        else:

            receiver = threading.Thread(target=self.receive_message_from_server, args=(transport, self.username))
            receiver.daemon = True
            receiver.start()

            user_interface = threading.Thread(target=self.user_interactions, args=(transport, self.username))
            user_interface.daemon = True
            user_interface.start()
            LOGGER.debug('Client processes started successfully')

            while True:
                time.sleep(1)
                if receiver.is_alive() and user_interface.is_alive():
                    continue
                break


if __name__ == '__main__':
    client = Client()
    client.start()
