import argparse
import json
import logging
import time
import inspect
import log.server_log_config
from socket import *

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
    s.listen(5)
    return s


@log
def process_message(message):
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
    server_log.warning('http 400 answered')
    return answer_400


@log
def process_request(s):
    client, addr = s.accept()

    # Получение сообщения от клиента
    data = client.recv(1000000)
    server_log.info('Request is %s', data.decode(ENCODING))

    message = json.loads(data)
    answer_json = json.dumps(process_message(message))
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
