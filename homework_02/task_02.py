"""
Попытался сделать более гибко, чтобы не зависеть от переданных параметров.
Не оптимально то, что весь файл грузится в память. Но на небольших данных это не важно.
"""

import json
import os

SOURCE_DIR = 'source_files'
FILE_NAME = 'orders.json'


def write_order_to_json(base_item, **kwargs):
    """
    Функция чтения JSON-файла и добавления в него объектов с переданными данными
    :param kwargs: пары ключ-значение для нового объекта
    :return: None
    """

    json_file_path = os.path.join(SOURCE_DIR, FILE_NAME)

    # чтение текущего файла
    with open(json_file_path, 'r') as f:
        data = json.load(f)

    # добавление нового объекта
    data[base_item].append(kwargs)

    # запись обновленных данных в файл
    with open(json_file_path, 'w') as f:
        json.dump(data, f, indent=4)


if __name__ == '__main__':
    write_order_to_json(base_item='orders', item='item1', quantity=2, price=100, buyer='Me', date='12.02.2022')
    write_order_to_json(base_item='orders', item='item2', buyer='He', date='12.02.2022')
    write_order_to_json(base_item='orders', item='item2', quantity=3, price=50, date='12.02.2022')
