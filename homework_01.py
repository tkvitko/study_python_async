
def show_result(source_list: list, show_len=False):
    for item in source_list:
        item_len = f'(len {len(item)})' if show_len else ''
        print(type(item), item, item_len)


if __name__ == '__main__':
    # 1. Каждое из слов «разработка», «сокет», «декоратор» представить в строковом формате и проверить тип и содержание
    # соответствующих переменных. Затем с помощью онлайн-конвертера преобразовать строковые представление в формат
    # Unicode и также проверить тип и содержимое переменных.

    words = ['разработка', 'сокет', 'декоратор']
    show_result(words)

    # https://unicode-table.com/ru/tools/decoder/
    words_unicode = [
        '\u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430',
        '\u0441\u043e\u043a\u0435\u0442',
        '\u0434\u0435\u043a\u043e\u0440\u0430\u0442\u043e\u0440'
    ]
    show_result(words_unicode)

    # 2. Каждое из слов «class», «function», «method» записать в байтовом типе без преобразования в последовательность
    # кодов (не используя методы encode и decode) и определить тип, содержимое и длину соответствующих переменных.

    words_binary = [b'class', b'function', b'method']
    show_result(words_binary, show_len=True)

    # 3. Определить, какие из слов «attribute», «класс», «функция», «type» невозможно записать в байтовом типе.

    # words = [b'attribute', b'класс', b'функция', b'type']
    # SyntaxError: bytes can only contain ASCII literal characters
