import os
import yaml

SOURCE_DIR = 'source_files'


def save_to_yml(data: dict, filename: str) -> None:
    """
    Функция сохранения данных в yaml-файл
    :param data: словарь для сохранения
    :param filename: имя файла для сохранения
    :return: None
    """

    with open(filename, 'w') as f:
        yaml.dump(data, f, allow_unicode=True, default_style=False)


def read_from_yml(filename: str) -> str:
    """
    Функция чтения данных из yaml-файла
    :param filename: имя файла для чтения
    :return: данные в виде строки
    """

    with open(filename, 'r') as f:
        return f.read()


if __name__ == '__main__':

    filename = 'file.yml'
    test_data = {
        'first': [0, 1, 2, 3],
        'second': 1,
        'third': {
            '1': '1€',
            '2': '2€'
        }
    }

    save_to_yml(data=test_data, filename=os.path.join(SOURCE_DIR, filename))
    print(read_from_yml(filename=os.path.join(SOURCE_DIR, filename)))
