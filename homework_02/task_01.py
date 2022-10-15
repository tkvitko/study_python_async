"""
Сделал более универсально, чем описано в задаче (без захардкоженных списков)
"""

import csv
import os
import re

import chardet

SOURCE_DIR = 'source_files'
SEARCH_STRINGS = [
    'Изготовитель системы',
    'Название ОС',
    'Код продукта',
    'Тип системы'
]


class NoDataInFile(Exception):
    def __init__(self, search_string, file_name):
        self.search_string = search_string
        self.file_name = file_name


def get_data(source_dir: str) -> list:
    """
    Функция парсинга файлов в заданной директории
    :param source_dir: название директории
    :return: список словарей спаршенных данных
    """

    extention = 'txt'

    files = list()
    for file in os.listdir(source_dir):
        if file.endswith(extention):
            files.append(file)

    result_list = list()

    for file in files:
        full_path = os.path.join(source_dir, file)

        # кодировка файла
        with open(full_path, 'rb') as fb:
            encoding = chardet.detect(fb.read())['encoding']

        # парсинг файла в словарь
        file_dict = dict()
        with open(full_path, encoding=encoding) as f:
            for line in f.readlines():
                line = line.strip()  # исключение переноса строки
                for search_string in SEARCH_STRINGS:
                    if re.search(search_string, line):
                        # если в строке нашлась подстрока поиска, заполняем словарь
                        file_dict[search_string] = re.sub(search_string + ':' + ' +', '', line)

        # Проверка, что полученные данные полны
        for search_string in SEARCH_STRINGS:
            if search_string not in file_dict.keys():
                raise NoDataInFile(search_string, file)

        result_list.append(file_dict)

    return result_list


def write_to_csv(target_file):
    """
    Функция записи данных в csv-файл
    :param target_file: имя файла для записи
    :return: None
    """
    data = get_data(source_dir=SOURCE_DIR)
    with open(target_file, 'w', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=SEARCH_STRINGS)
        writer.writeheader()
        for row in data:
            writer.writerow(row)


if __name__ == '__main__':
    csv_file = 'result_01.csv'
    try:
        write_to_csv(os.path.join(SOURCE_DIR, csv_file))
    except NoDataInFile as e:
        print(f'Ошибка: нет строки во входном файле: {e}')
