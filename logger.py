import parameters


class Colors:
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def colored(text, *colors):
        return ''.join(colors) + str(text) + Colors.ENDC

    @staticmethod
    def disable():
        Colors.OKBLUE = ''
        Colors.OKGREEN = ''
        Colors.FAIL = ''
        Colors.ENDC = ''
        Colors.BOLD = ''
        Colors.UNDERLINE = ''


def handle_error(message):
    print(Colors.colored(message, Colors.FAIL, Colors.BOLD))


def print_info(message):
    print(Colors.colored(message, Colors.OKBLUE, Colors.BOLD))


def print_debug_info(*message):
    print(Colors.colored(" ".join(message), Colors.OKGREEN))


def log(func):
    def wrapper(*args, **kwargs):
        func_str = func.__name__
        args_str = ', '.join(args)
        # kwargs_str = ', '.join([':'.join([str(j) for j in i]) for i in kwargs.iteritems()])
        print("Function:", func_str, "args:", args_str)
        # print(kwargs_str)
        return func(*args, **kwargs)

    return wrapper
