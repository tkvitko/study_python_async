import logging
import argparse
import sys
from PyQt5.QtWidgets import QApplication

from functions import log
from constants import DEFAULT_IP, DEFAULT_PORT, ServerError
from client_transport import ClientTransport
from client_ui import ClientMainWindow
from client_start_dialog import UserNameDialog

# Инициализация клиентского логера
logger = logging.getLogger('client')


# Парсер аргументов коммандной строки
@log
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--addr', '-a', help="ip address to listen on", type=str, default=DEFAULT_IP)
    parser.add_argument('--port', '-p', help="tcp port to listen on", type=int, default=DEFAULT_PORT)
    parser.add_argument('--name', '-n', help="user name", type=str, default=None)
    args = parser.parse_args()
    server_addr = args.addr
    server_port = args.port
    username = args.name

    return server_addr, server_port, username


# Основная функция клиента
if __name__ == '__main__':

    server_address, server_port, client_name = arg_parser()
    client_app = QApplication(sys.argv)

    if not client_name:
        start_dialog = UserNameDialog()
        client_app.exec_()
        if start_dialog.ok_pressed:
            client_name = start_dialog.client_name.text()
            password = start_dialog.password.text()
            del start_dialog
        else:
            exit(0)

    logger.info(
        f'Запущен клиент с параметрами: адрес сервера: {server_address} , порт: {server_port}, имя пользователя: {client_name}')

    try:
        transport = ClientTransport(server_address, server_port, client_name, password)
    except ServerError as error:
        print(error.text)
        exit(1)
    transport.setDaemon(True)
    transport.start()

    # Создаём GUI
    main_window = ClientMainWindow(transport)
    main_window.make_connection(transport)
    main_window.setWindowTitle(f'Чат Программа alpha release - {client_name}')
    client_app.exec_()

    # Раз графическая оболочка закрылась, закрываем транспорт
    transport.transport_shutdown()
    transport.join()
