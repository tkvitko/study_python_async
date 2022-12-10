import json
import logging
import socket
import sys
import threading
import time
import hashlib

from PyQt5.QtCore import QObject, pyqtSignal

from chat.functions import receive_message, send_message
from chat.metaclasses import ClientVerifier
from chat.constants import ServerError

LOGGER = logging.getLogger('client')
socket_lock = threading.Lock()


class ClientTransport(threading.Thread, QObject):  # , metaclass=ClientVerifier):

    new_message = pyqtSignal(str)
    connection_lost = pyqtSignal()

    # @log
    def __init__(self, server_addr, server_port, username, password):
        threading.Thread.__init__(self)
        QObject.__init__(self)

        self.server_addr = server_addr
        self.server_port = server_port
        self.username = username
        self.password = password
        self.transport = None
        self.all_users, self.contacts = self.connect_to_server()
        self.running = True

    # @log
    # @staticmethod
    def send_message(self, to, text):
        message_dict = {
            'action': 'message',
            'from': self.username,
            'to': to,
            'time': time.time(),
            'message_text': text,
            'token': 'random'
        }
        LOGGER.debug(f'Dict message here: {message_dict}')
        try:
            with socket_lock:
                send_message(self.transport, message_dict)
                LOGGER.info(f'Message sent to {message_dict["to"]}')
        except:
            LOGGER.critical('Connection with server lost')
            sys.exit(1)

    def add_contact(self, account_name):
        message_dict = {
            'action': 'add_contact',
            'account_name': self.username,
            'user_id': account_name,
            'time': time.time(),
            'token': 'random'
        }
        LOGGER.debug(f'Dict message here: {message_dict}')
        try:
            with socket_lock:
                send_message(self.transport, message_dict)
                print(message_dict)
                LOGGER.info(f'{message_dict["user_id"]} has been added to contact list')
        except:
            LOGGER.critical('Connection with server lost 1')
            sys.exit(1)

    def delete_contact(self, account_name):
        message_dict = {
            'action': 'del_contact',
            'account_name': self.username,
            'user_id': account_name,
            'time': time.time(),
            'token': 'random'
        }
        LOGGER.debug(f'Dict message here: {message_dict}')
        try:
            with socket_lock:
                send_message(self.transport, message_dict)
                LOGGER.info(f'{message_dict["user_id"]} has been deleted from contact list')
        except:
            LOGGER.critical('Connection with server lost 2')
            sys.exit(1)

    def get_messages(self, account_name, to):
        """Функция генерирует запрос списка сообщений"""
        message_dict = {
            'action': 'get_messages',
            'time': time.time(),
            'account_name': account_name,
            'to': to,
            'token': 'random'
        }
        try:
            with socket_lock:
                send_message(self.transport, message_dict)
                messages = self.process_response_ans(receive_message(self.transport))
                LOGGER.info(f'Get messages request message has been sent for {account_name} and {to}')
                return messages
        except:
            LOGGER.critical('Connection with server lost 3')
            sys.exit(1)

    # @log
    @staticmethod
    def create_presence(account_name, password):
        """Функция генерирует запрос о присутствии клиента"""

        h = hashlib.sha256()
        h.update(password.encode('ascii'))
        password_hash = h.hexdigest()

        presence_body = {
            'action': 'presence',
            'time': time.time(),
            'user': {
                'account_name': account_name,
                'password_hash': password_hash
            }
        }
        LOGGER.debug(f'Presence has been created for {account_name}')
        return presence_body

    def get_contact_list(self, account_name):
        """Функция генерирует запрос списка контактов"""
        message_dict = {
            'action': 'get_contacts',
            'time': time.time(),
            'account_name': account_name,
            'token': 'random'
        }
        try:
            with socket_lock:
                send_message(self.transport, message_dict)
                contacts = self.process_response_ans(receive_message(self.transport))
                LOGGER.info(f'Get contacts request message has been sent for {account_name}')
                return contacts
        except:
            LOGGER.critical('Connection with server lost 4')
            sys.exit(1)

    def get_users_list(self, account_name):
        """Функция генерирует запрос списка контактов"""
        message_dict = {
            'action': 'get_users',
            'time': time.time(),
            'account_name': account_name,
            'token': 'random'
        }
        try:
            with socket_lock:
                send_message(self.transport, message_dict)
                contacts = self.process_response_ans(receive_message(self.transport))
                LOGGER.info(f'Get users request message has been sent for {account_name}')
                return contacts
        except:
            LOGGER.critical('Connection with server lost 5')
            sys.exit(1)

    @staticmethod
    def print_help():
        print('Commands list:')
        print('message - send message to user')
        print('add - add contact')
        print('help - this help')
        print('exit - close client')

    # @log
    @staticmethod
    def process_response_ans(message):
        LOGGER.debug(f'Разбор приветственного сообщения от сервера: {message}')
        if 'response' in message:
            if message['response'] == 200:
                return '200 : OK'
            elif message['response'] == 202:
                return message['alert']
            elif message['response'] == 400:
                raise ServerError(f'400 : {message["error"]}')
            elif message['response'] == 403:
                raise ServerError(f'403 : {message["error"]}')

    def connect_to_server(self):
        print('Client started')

        LOGGER.info(
            f'Client started: server is {self.server_addr}:{self.server_port}, username is: {self.username}')

        try:
            self.transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.transport.connect((self.server_addr, self.server_port))
            presence_message = self.create_presence(self.username, self.password)
            send_message(self.transport, presence_message)
            answer = self.process_response_ans(receive_message(self.transport))
            LOGGER.info(f'Connected to server. Server answer: {answer}')
            print(f'Connected to server. Server answer: {answer}')

            contacts_list = self.get_contact_list(self.username)
            LOGGER.info(f'Connected to server. contacts_list: {contacts_list}')
            print(f'Connected to server. contacts_list: {contacts_list}')

            users_list = self.get_users_list(self.username)
            LOGGER.info(f'Connected to server. users_list: {users_list}')
            print(f'Connected to server. users_list: {users_list}')

            return users_list, contacts_list

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

    def transport_shutdown(self):
        self.running = False
        exit_message = {
            'action': 'exit',
            'time': time.time(),
            'account_name': self.username,
            'token': 'random'
        }
        with socket_lock:
            send_message(self.transport, exit_message)
        print('Connection closed')
        LOGGER.info('Connection closed by user')
        time.sleep(0.5)

    def run(self):
        while self.running:
            time.sleep(1)
            with socket_lock:
                try:
                    self.transport.settimeout(0.5)
                    message = receive_message(self.transport)
                except OSError as err:
                    if err.errno:
                        LOGGER.critical(f'Потеряно соединение с сервером.')
                        self.running = False
                        self.connection_lost.emit()
                # Проблемы с соединением
                except (ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError, TypeError):
                    LOGGER.debug(f'Потеряно соединение с сервером.')
                    self.running = False
                    self.connection_lost.emit()
                else:
                    self.process_response_ans(message)
                    if 'action' in message and message['action'] == 'message' and 'from' in message and 'to' in message \
                            and 'message_text' in message:  # and message['to'] == me:
                        print(f'\nMessage received from {message["from"]}: \n{message["message_text"]}')
                        LOGGER.info(f'\nMessage received from {message["from"]}: \n{message["message_text"]}')
                        self.new_message.emit(message['from'])
                    else:
                        LOGGER.error(f'Wrong message received from server: {message}')
                finally:
                    self.transport.settimeout(5)  # зачем?
