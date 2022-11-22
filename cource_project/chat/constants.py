import time


DEFAULT_PORT = 8080
DEFAULT_IP = '0.0.0.0'
MAX_CONNECTIONS = 5
MAX_PACKAGE_LENGTH = 1024
ENCODING = 'utf-8'

ANSWER_200 = {
    'response': 200,
    "time": time.time()
}
ANSWER_400 = {
    'response': 400,
    "time": time.time()
}
