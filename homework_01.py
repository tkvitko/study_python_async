import subprocess
import chardet


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

    words = ['attribute', 'класс', 'функция', 'type']
    for word in words:
        try:
            print(bytes(word, encoding='ascii'))
        except UnicodeEncodeError:
            print(f'Строку {word} нельзя записать в байтовом виде')

    # 4. Преобразовать слова «разработка», «администрирование», «protocol», «standard» из строкового представления
    # в байтовое и выполнить обратное преобразование (используя методы encode и decode).

    words = ['разработка', 'администрирование', 'protocol', 'standart']
    print(words)

    words_encoded = []
    for word in words[:]:
        words_encoded.append(word.encode(encoding='utf-8', errors='ignore'))
    print(words_encoded)

    words_decoded = []
    for word in words_encoded[:]:
        words_decoded.append(word.decode(encoding='utf-8', errors='ignore'))
    print(words_decoded)

    # 5. Выполнить пинг веб-ресурсов yandex.ru, youtube.com и преобразовать результаты из байтовового в строковый тип
    # на кириллице.

    hosts = ['yandex.ru', 'youtube.com']
    max_count = 3

    for host in hosts:
        args = ['ping', host]
        ping_yandex = subprocess.Popen(args, stdout=subprocess.PIPE)

        count = 0
        string_encoding = None
        for line in ping_yandex.stdout:
            if count <= max_count:
                if string_encoding is None:
                    string_encoding = chardet.detect(line)['encoding']
                l = line.decode(encoding=string_encoding)
                print(type(l), l)
                count += 1
            else:
                break

    # 6. Создать текстовый файл test_file.txt, заполнить его тремя строками: «сетевое программирование», «сокет»,
    # «декоратор». Проверить кодировку файла по умолчанию. Принудительно открыть файл в формате Unicode и вывести его
    # содержимое.

    source_file = 'test_file.txt'

    # узнать кодировку файла
    with open(source_file, 'rb') as fb:
        file_encoding = chardet.detect(fb.read())['encoding']

    with open(source_file, 'r', encoding=file_encoding) as f:
        for line in f.readlines():
            print(line)
