"""
Очень странное задание.
Еще в прошлом ДЗ был сделан многопоточный клиент для обеих функций.
Потому выполняю только b)
"""

import subprocess


def start_clients(number: int = 2):
    processes = list()
    while True:
        accept = input('Запускаем? ')
        if accept == 'yes':
            for i in range(number):
                processes.append(subprocess.Popen('python client.py', shell=True))


if __name__ == '__main__':
    start_clients(number=5)
