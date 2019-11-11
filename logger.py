import parameters
import itertools

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


def handle_error(*args, sep=' ', end='\n'):
    print(Colors.colored(sep.join(args) + end, Colors.FAIL, Colors.BOLD))


def print_info(*args, sep=' ', end='\n'):
    to_print = sep.join(str(arg) for arg in args) + end
    print(Colors.colored(to_print, Colors.OKBLUE, Colors.BOLD), end='')


def print_debug_info(*args, sep=' ', end='\n'):
    to_print = sep.join(str(arg) for arg in args) + end
    if parameters.verbose:
        print(Colors.colored(to_print, Colors.OKGREEN), end='')


def log(func):
    def wrapper(*args, **kwargs):
        func_str = func.__name__
        args_str = ', '.join([str(arg) for arg in args])
        kwargs_str = ', '.join([':'.join([str(j) for j in i]) for i in kwargs.values()])
        if parameters.verbose:
            print_debug_info("Function:", func_str, "args:", args_str, "kwargs:", kwargs_str)
        return func(*args, **kwargs)

    return wrapper
