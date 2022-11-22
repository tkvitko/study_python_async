import socket
import argparse
import logging
import select
import chat.client_log_config
from chat.constants import MAX_CONNECTIONS, ANSWER_200, ANSWER_400, DEFAULT_IP, DEFAULT_PORT
from chat.functions import receive_message, send_message, log

LOGGER = logging.getLogger('server')


@log
def process_message_from_client(message, messages_list,
                                client, clients, usernames):

    LOGGER.debug(f'New message from client : {message}')

    # Client connection
    if 'action' in message and message['action'] == 'presence' and 'time' in message and 'user' in message:
        if message['user']['account_name'] not in usernames.keys():
            usernames[message['user']['account_name']] = client
            send_message(client, ANSWER_200)
        else:
            response = ANSWER_400
            response['error'] = 'There is already user with this username'
            send_message(client, response)
            clients.remove(client)
            client.close()
        return

    # Message from client
    elif 'action' in message and message['action'] == 'message' and \
            'to' in message and 'time' in message and 'from' in message and 'message_text' in message:
        messages_list.append(message)
        return

    # Client disconnection
    elif 'action' in message and message['action'] == 'exit' and 'account_name' in message:
        clients.remove(usernames[message['account_name']])
        usernames[message['account_name']].close()
        del usernames[message['account_name']]
        return

    # Bad request
    else:
        response = ANSWER_400
        response['errpr'] = 'Bad request'
        send_message(client, response)
        return


# @log
def resend_message_to_user(message, usernames, listen_socks):

    if message['to'] in usernames:
        if usernames[message['to']] in listen_socks:
            send_message(usernames[message['to']], message)
            LOGGER.info(f'Sent message to user {message["to"]} from user {message["from"]}.')
        else:
            raise ConnectionError
    else:
        LOGGER.error(f'User {message["to"]} is not online')


@log
def get_params():
    parser = argparse.ArgumentParser()
    parser.add_argument('--addr', '-a', help="ip address to listen on", type=str, default=DEFAULT_IP)
    parser.add_argument('--port', '-p', help="tcp port to listen on", type=int, default=DEFAULT_PORT)
    args = parser.parse_args()
    addr = args.addr
    port = args.port

    return addr, port


def main():
    listen_address, listen_port = get_params()

    LOGGER.info(f'Server started: {listen_address}:{listen_port}')
    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.bind((listen_address, listen_port))
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
                    process_message_from_client(message, messages_queue,
                                                client_with_message, clients, users)
                except Exception:
                    LOGGER.info(f'Client disconnected {client_with_message.getpeername()}')
                    clients.remove(client_with_message)

        for message in messages_queue:
            try:
                resend_message_to_user(message, users, send_data_lst)
            except Exception:
                LOGGER.info(f'Client disconnected {message["to"]}')
                clients.remove(users[message['to']])
                del users[message['to']]
        messages_queue.clear()


if __name__ == '__main__':
    main()
