import os
import socket
import argparse
import logging
import select
from datetime import datetime
from logging import handlers

from chat_backend.constants import MAX_CONNECTIONS, ANSWER_200, ANSWER_400, DEFAULT_IP, DEFAULT_PORT, ANSWER_202, ANSWER_403
from functions.functions import receive_message, send_message#, log
from chat_backend.descriptors import Port
from functions.metaclasses import ServerVerifier

from chat_backend.db import ServerDatabase

LOG_DIR = 'logs'
log_format = logging.Formatter('%(asctime)s %(module)s %(levelname)s %(message)s')
server_log_handler = handlers.TimedRotatingFileHandler(filename=os.path.join(LOG_DIR, 'server.log'),
                                                       when='D',
                                                       interval=1,
                                                       backupCount=2)
LOGGER = logging.getLogger('server')
LOGGER.setLevel(logging.DEBUG)
LOGGER.addHandler(server_log_handler)


class Server(metaclass=ServerVerifier):
    port = Port()
    db = ServerDatabase()

    # @log
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--addr', '-a', help="ip address to listen on", type=str, default=DEFAULT_IP)
        parser.add_argument('--port', '-p', help="tcp port to listen on", type=int, default=DEFAULT_PORT)
        args = parser.parse_args()
        self.addr = args.addr
        self.port = args.port

    # @login_required
    def process_message_from_client(self, message, messages_list,
                                    client, clients, usernames):

        LOGGER.info(f'New message from client : {message}')

        # Client connection
        if 'action' in message and message['action'] == 'presence' and 'time' in message and 'user' in message:
            if message['user']['account_name'] not in usernames.keys():
                usernames[message['user']['account_name']] = client
                client_ip, client_port = client.getpeername()
                user_exists = self.db.check_user_exists(message['user']['account_name'])
                if not user_exists:
                    self.db.add_user(login=message['user']['account_name'],
                                     ip=client_ip,
                                     password_hash=message['user']['password_hash'])
                    send_message(client, ANSWER_200)
                else:
                    authorized = self.db.check_users_password_hash(user_login=message['user']['account_name'],
                                                                   password_hash=message['user']['password_hash'])
                    if authorized:
                        self.db.set_user_status(message['user']['account_name'], is_online=True)
                        send_message(client, ANSWER_200)
                    else:
                        response = ANSWER_403
                        response['error'] = 'Wrong password'
                        send_message(client, response)
                        LOGGER.debug(f"Response: {response}")
            else:
                response = ANSWER_400
                response['error'] = 'There is already user with this username'
                send_message(client, response)
                clients.remove(client)
                client.close()

        # Message from client
        elif 'action' in message and message['action'] == 'message' and \
                'to' in message and 'time' in message and 'from' in message and 'message_text' in message:
            messages_list.append(message)
            self.db.save_message(from_user=message['from'],
                                 to_user=message['to'],
                                 text=message['message_text'],
                                 time=datetime.now())
            return

        # Client disconnection
        elif 'action' in message and message['action'] == 'exit' and 'account_name' in message:
            clients.remove(usernames[message['account_name']])
            self.db.set_user_status(message['account_name'], is_online=False)
            usernames[message['account_name']].close()
            del usernames[message['account_name']]
            return

        # Get messages history
        elif 'action' in message and message[
            'action'] == 'get_messages' and 'account_name' in message and 'to' in message:
            messages = self.db.get_messages_from_db(message['account_name'], message['to'])
            answer = ANSWER_202
            answer['alert'] = messages
            print(answer)
            send_message(client, answer)
            LOGGER.debug(f"Response: {answer}")

        # Get contacts
        elif 'action' in message and message['action'] == 'get_contacts' and 'account_name' in message:
            contacts = self.db.get_user_contacts(message['account_name'])
            answer = ANSWER_202
            answer['alert'] = contacts
            send_message(client, answer)
            LOGGER.debug(f"Response: {answer}")

        # Get all users
        elif 'action' in message and message['action'] == 'get_users' and 'account_name' in message:
            users = [user[0] for user in self.db.get_users()]
            answer = ANSWER_202
            answer['alert'] = users
            send_message(client, answer)
            LOGGER.debug(f"Response: {answer}")

        # Add contact
        elif 'action' in message and message[
            'action'] == 'add_contact' and 'account_name' in message and 'user_id' in message:
            self.db.add_contact_for_user(message['account_name'], message['user_id'])
            send_message(client, ANSWER_200)
            LOGGER.debug(f"Response: {ANSWER_200}")

        # Delete contact
        elif 'action' in message and message[
            'action'] == 'del_contact' and 'account_name' in message and 'user_id' in message:
            self.db.remove_contact_from_user(message['account_name'], message['user_id'])
            send_message(client, ANSWER_200)
            LOGGER.debug(f"Response: {ANSWER_200}")

        # Bad request
        else:
            response = ANSWER_400
            response['error'] = 'Bad request'
            send_message(client, response)
            LOGGER.debug(f"Response: {response}")
            return

    # @log
    @staticmethod
    def resend_message_to_user(message, usernames, listen_socks):

        if message['to'] in usernames:
            if usernames[message['to']] in listen_socks:
                send_message(usernames[message['to']], message)
                LOGGER.info(f'Sent message to user {message["to"]} from user {message["from"]}: message {message}')
            else:
                raise ConnectionError
        else:
            LOGGER.error(f'User {message["to"]} is not online')

    def start(self):
        LOGGER.info(f'Server started: {self.addr}:{self.port}')
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.bind((self.addr, self.port))
        transport.settimeout(0.5)

        clients = []
        messages_queue = []
        users = {}

        transport.listen(MAX_CONNECTIONS)
        while True:
            try:
                client, client_address = transport.accept()
            except OSError:
                pass
            else:
                LOGGER.info(f'Client connected: {client_address}')
                clients.append(client)

            recv_data_lst = []
            send_data_lst = []
            err_lst = []

            try:
                if clients:
                    recv_data_lst, send_data_lst, err_lst = select.select(clients, clients, [], 0)
            except OSError:
                pass

            if recv_data_lst:
                for client_with_message in recv_data_lst:
                    try:
                        message = receive_message(client_with_message)
                        self.process_message_from_client(message, messages_queue,
                                                         client_with_message, clients, users)
                    except Exception:
                        LOGGER.info(f'Client disconnected {client_with_message.getpeername()}')
                        clients.remove(client_with_message)

            for message in messages_queue:
                try:
                    self.resend_message_to_user(message, users, send_data_lst)
                except Exception:
                    LOGGER.info(f'Client disconnected {message["to"]}')
                    clients.remove(users[message['to']])
                    del users[message['to']]
            messages_queue.clear()


if __name__ == '__main__':
    server = Server()
    server.start()
