class Port:
    def __set__(self, instance, value):
        if value < 0 or not isinstance(value, int):
            print(f'Bad port: {value}')
            exit(1)
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name
