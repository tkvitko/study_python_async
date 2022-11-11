import argparse
import json
import logging
import time
import log.client_log_config
from socket import *

ENCODING = 'utf-8'
client_log = logging.getLogger('client')


def get_params():
    parser = argparse.ArgumentParser()
    parser.add_argument('--addr', '-a', help="ip address to connect with", type=str)
    parser.add_argument('--port', '-p', help="tcp port to connect with", type=int, default=7777)
    args = parser.parse_args()
    addr = args.addr
    port = args.port

    return addr, port


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
    data = s.recv(1000000)
    return data.decode(ENCODING)


def send_presence_to_server(server_ip: str, server_port: int):
    s = start_client(server_ip=server_ip, server_port=server_port)
    client_log.info('Client started')
    sent_message = send_presence_message(s)
    client_log.info(sent_message)
    s.close()


if __name__ == '__main__':

    addr, port = get_params()

    try:
        send_presence_to_server(server_ip=addr,
                                server_port=port)
    except Exception as e:
        client_log.error("Can't start client: %s", e)
