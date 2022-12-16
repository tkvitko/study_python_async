import dis


class ClientVerifier(type):
    def __init__(self, class_name, bases, class_dict):
        forbidden_methods = ['accept', 'listen']#, 'socket']
        methods = []
        for function in class_dict:
            try:
                instructions = dis.get_instructions(class_dict[function])
            except TypeError:
                pass
            else:
                for instruction in instructions:
                    if instruction.opname == 'LOAD_GLOBAL':
                        if instruction.argval not in methods:
                            methods.append(instruction.argval)

        for command in forbidden_methods:
            if command in methods:
                raise TypeError('В классе обнаружено использование запрещённого метода')
        # Вызов get_message или send_message из utils считаем корректным использованием сокетов
        if 'get_message' in methods or 'send_message' in methods:
            pass
        else:
            raise TypeError('Отсутствуют вызовы функций, работающих с сокетами.')

        super().__init__(class_name, bases, class_dict)


class ServerVerifier(type):
    def __init__(self, class_name, bases, class_dict):
        methods = []
        attrs = []

        for function in class_dict:
            try:
                instructions = dis.get_instructions(class_dict[function])
            except TypeError:
                pass
            else:
                for instruction in instructions:
                    if instruction.opname == 'LOAD_GLOBAL':
                        if instruction.argval not in methods:
                            methods.append(instruction.argval)
                    elif instruction.opname == 'LOAD_ATTR':
                        if instruction.argval not in attrs:
                            attrs.append(instruction.argval)

        if 'connect' in methods:
            raise TypeError('Использование метода connect недопустимо в серверном классе')
        if not ('SOCK_STREAM' in attrs and 'AF_INET' in attrs):
            raise TypeError('Некорректная инициализация сокета.')

        super().__init__(class_name, bases, class_dict)
