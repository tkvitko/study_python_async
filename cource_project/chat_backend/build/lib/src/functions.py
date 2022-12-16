import json
import logging
import socket

from chat_backend.src.constants import MAX_PACKAGE_LENGTH, ENCODING

functions_log = logging.getLogger('functions')


def receive_message(sender: socket) -> dict:
    """Receive and return message from socket"""
    message_encoded = sender.recv(MAX_PACKAGE_LENGTH)
    message = message_encoded.decode(ENCODING)
    return json.loads(message)


def send_message(sock, message):
    """Get socket and message, send message to socket"""
    message = json.dumps(message)
    message_encoded = message.encode(ENCODING)
    sock.send(message_encoded)


def log(func):
    def wrapper(*args, **kwargs):
        functions_log.info('Function %s %s called from function "%s"', func.__name__, args, func.__module__)
        return func(*args, **kwargs)

    return wrapper
