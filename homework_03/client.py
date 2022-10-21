import argparse
import json
import time
from socket import *

ENCODING = 'utf-8'


def send_presence_to_server(server_ip: str, server_port: int):
    s = socket(AF_INET, SOCK_STREAM)
    s.connect((server_ip, server_port))

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
    print(data.decode(ENCODING))
    s.close()


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--addr', '-a', help="ip address to connect with", type=str)
    parser.add_argument('--port', '-p', help="tcp port to connect with", type=int, default=7777)
    args = parser.parse_args()
    addr = args.addr
    port = args.port

    try:
        send_presence_to_server(server_ip=addr,
                                server_port=port)
    except Exception as e:
        print(e)
