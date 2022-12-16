def check_if_token_valid(token: str) -> bool:
    """
    Функция на будущее. Будет проверять валидность токена после того, как будет реализована вся система авторизации:
    - генерация токена для клиента после успешной авторизации
    - сохранение токена в БД, отдача токена клиенту
    - механизм протухания токена
    - отправка токена клиентом в каждом запросе
    """

    return True


def login_required(func):
    def checker(*args, **kwargs):

        authorised = False

        for arg in args:
            if isinstance(arg, dict):
                if 'action' in arg:
                    if arg['action'] == 'presence':
                        authorised = True
                    elif 'token' in arg:
                        authorised = check_if_token_valid(arg['token'])

        if not authorised:
            raise TypeError

        return func(*args, **kwargs)

    return checker
