import argparse
import json
import time
from socket import *

ENCODING = 'utf-8'


def start_server(server_ip: str, server_port: int):
    # Поднятие слушателя
    s = socket(AF_INET, SOCK_STREAM)
    s.bind((server_ip, server_port))
    s.listen(5)

    while True:
        client, addr = s.accept()

        # Получение сообщения от клиента
        data = client.recv(1000000)
        print(data.decode(ENCODING))

        answer_200 = {
            "response": 200,
            "time": time.time()
        }

        answer_400 = {
            "response": 400,
            "time": time.time()
        }

        message = json.loads(data)
        if 'action' in message.keys() and message['action'] == 'presence':
            answer_json = json.dumps(answer_200)
        else:
            answer_json = json.dumps(answer_400)

        client.send(answer_json.encode(ENCODING))
        client.close()


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--addr', '-a', help="ip address to listen on", type=str, default='0.0.0.0')
    parser.add_argument('--port', '-p', help="tcp port to listen on", type=int, default=7777)
    args = parser.parse_args()
    addr = args.addr
    port = args.port

    try:
        start_server(server_ip=addr,
                     server_port=port)
    except Exception as e:
        print(e)
