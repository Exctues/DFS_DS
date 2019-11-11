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


def print_debug_info(message):
    print(Colors.colored(message, Colors.OKGREEN))
