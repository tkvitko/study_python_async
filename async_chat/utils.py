import json

ENCODING = 'utf-8'


def get_message(client):
    encoded_response = client.recv(10000000)
    json_response = encoded_response.decode(ENCODING)
    response = json.loads(json_response)
    return response


def send_message(s, message):
    js_message = json.dumps(message)
    encoded_message = js_message.encode(ENCODING)
    s.send(encoded_message)
