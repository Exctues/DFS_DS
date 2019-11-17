from utils import parameters


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
        kwargs_str = ', '.join([str(k) + ':' + str(v) for k, v in kwargs.items()])

        res = func(*args, **kwargs)

        info = "\nFUNCTION {}:: {}; {}".format(func_str, 
                                               (Colors.colored("args: ", Colors.UNDERLINE) + args_str)
                                               if args else "", 
                                               (Colors.colored("kwargs: ", Colors.UNDERLINE) + kwargs_str) 
                                               if kwargs else "")

        print_debug_info(info)
        print_debug_info("RES", res, '\n')
        return res

    return wrapper
