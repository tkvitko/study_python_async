import argparse
import json
import logging
import select
import time
import inspect
import log.server_log_config
from socket import *
from utils import get_message, send_message

ENCODING = 'utf-8'
server_log = logging.getLogger('server')


def log(func):
    def wrapper(*args, **kwargs):
        # получение имени вызвавшей функции:
        current_frame = inspect.currentframe()
        caller_frame = current_frame.f_back
        code_obj = caller_frame.f_code
        code_obj_name = code_obj.co_name

        server_log.info('Function %s %s called from function "%s"', func.__name__, args, code_obj_name)
        return func(*args, **kwargs)

    return wrapper


@log
def get_params():
    parser = argparse.ArgumentParser()
    parser.add_argument('--addr', '-a', help="ip address to listen on", type=str, default='0.0.0.0')
    parser.add_argument('--port', '-p', help="tcp port to listen on", type=int, default=7777)
    args = parser.parse_args()
    addr = args.addr
    port = args.port

    return addr, port


@log
def start_listener(server_ip: str, server_port: int):
    # Поднятие слушателя
    s = socket(AF_INET, SOCK_STREAM)
    s.bind((server_ip, server_port))
    s.settimeout(0.5)
    s.listen(5)
    return s


@log
def process_message(message, messages):
    answer_200 = {
        "response": 200,
        "time": time.time()
    }

    answer_400 = {
        "response": 400,
        "time": time.time()
    }

    if 'action' in message.keys() and message['action'] == 'presence':
        server_log.info('http 200 answered')
        return answer_200
    elif 'action' in message.keys() and message['action'] == 'message':
        messages.append(message['account_name'], message['text'])
        return
    server_log.warning('http 400 answered')
    return answer_400


@log
def process_request(s):
    clients = []
    messages = []

    try:
        client, addr = s.accept()
    except OSError:
        pass
    else:
        server_log.info(f'client connected: {addr}')
        clients.append(client)

    recv_data_lst = []
    send_data_lst = []
    err_lst = []
    # Проверяем на наличие ждущих клиентов
    try:
        if clients:
            recv_data_lst, send_data_lst, err_lst = select.select(clients, clients, [], 0)
    except OSError:
        pass

    # приём сообщений
    if recv_data_lst:
        for client_with_message in recv_data_lst:
            try:
                process_client_message(get_message(client_with_message),
                                       messages, client_with_message)
            except:
                server_log.info(f'client disconnected {client_with_message.getpeername()}')
                clients.remove(client_with_message)

    # отправка сообщений
    if messages and send_data_lst:
        message = {
            'action': 'message',
            'sender': messages[0][0],
            'time': time.time(),
            'text': messages[0][1]
        }
        del messages[0]
        for waiting_client in send_data_lst:
            try:
                send_message(waiting_client, message)
            except:
                server_log.info(f'client dicsonnected: {waiting_client.getpeername()}')
                clients.remove(waiting_client)


@log
def process_client_message(data, messages, client):
    server_log.info('Request is %s', data.decode(ENCODING))

    message = json.loads(data)
    answer_json = json.dumps(process_message(message, messages))
    server_log.info('Answer is %s', answer_json)

    client.send(answer_json.encode(ENCODING))
    client.close()


@log
def start_server(server_ip: str, server_port: int):
    s = start_listener(server_ip=server_ip, server_port=server_port)
    server_log.info('Server started')

    while True:
        process_request(s)


if __name__ == '__main__':

    addr, port = get_params()

    try:
        start_server(server_ip=addr,
                     server_port=port)
    except Exception as e:
        server_log.error("Can't start server: %s", e)
