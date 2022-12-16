import argparse
import json
import logging
import sys
import time
import log.client_log_config
from socket import *
from utils import get_message, send_message

ENCODING = 'utf-8'
client_log = logging.getLogger('client')


def get_params():
    parser = argparse.ArgumentParser()
    parser.add_argument('--addr', '-a', help="ip address to connect with", type=str)
    parser.add_argument('--port', '-p', help="tcp port to connect with", type=int, default=7777)
    parser.add_argument('--mode', '-m', help="send or receive", type=str, default='send')
    args = parser.parse_args()
    addr = args.addr
    port = args.port
    mode = args.mode

    return addr, port, mode


def start_client(server_ip: str, server_port: int):
    s = socket(AF_INET, SOCK_STREAM)
    s.connect((server_ip, server_port))
    client_log.info('Connected to server %s', server_ip)

    return s


def send_presence_message(s):
    presence_message_dict = {
        "action": "presence",
        "time": time.time(),
        "type": "status",
        "user": {
            "account_name": "tkvitko",
            "status": "online"}
    }

    presence_message_json = json.dumps(presence_message_dict)
    s.send(presence_message_json.encode(ENCODING))
    data = s.recv(10000000)
    return data.decode(ENCODING)


def interact_with_server(server_ip: str, server_port: int, client_mode: str):
    s = start_client(server_ip=server_ip, server_port=server_port)
    client_log.info('Client started')
    sent_message = send_presence_message(s)
    client_log.info(sent_message)

    if client_mode == 'send':
        print('sending mode')
    else:
        print('receiving mode')

    while True:
        # режим работы - отправка сообщений
        if client_mode == 'send':
            try:
                send_message(s, create_message_from_user_input(s))
            except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                client_log.error(f'Connection with server {server_ip} lost')
                sys.exit(1)

        # Режим работы приём:
        if client_mode == 'listen':
            try:
                message_from_server(get_message(s))
            except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                client_log.error(f'Connection with server {server_ip} lost')
                sys.exit(1)


def create_message_from_user_input(sock, account_name='Guest'):
    message = input('Введите сообщение для отправки или \'!!!\' для завершения работы: ')
    if message == '!!!':
        sock.close()
        sys.exit(0)
    else:
        message_dict = {
            'action': 'message',
            'time': time.time(),
            'account_name': account_name,
            'text': message
        }
        print(message_dict)
        client_log.debug(f'message dict has been created: {message_dict}')
        return message_dict


def message_from_server(message):
    """Функция - обработчик сообщений других пользователей, поступающих с сервера"""
    if 'actions' in message and message['action'] == 'message' and 'sender' in message and 'text' in message:
        print(f'Получено сообщение от пользователя '
              f'{message["sender"]}:\n{message["text"]}')
        client_log.info(f'Получено сообщение от пользователя '
                        f'{message["sender"]}:\n{message["text"]}')
    else:
        client_log.error(f'Bad message from server: {message}')


if __name__ == '__main__':

    addr, port, mode = get_params()

    try:
        interact_with_server(server_ip=addr,
                             server_port=port,
                             client_mode=mode)
    except Exception as e:
        client_log.error("Can't start client: %s", e)
