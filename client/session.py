from client.utils import *


class Session:
    def __init__(self, interactive=True):
        self.__wd = "/"
        self.interactive = interactive

    def print_curr_dir(self, *args):
        print(Colors.colored(self.get_curr_dir(), Colors.OKBLUE, Colors.BOLD))

    def get_curr_dir(self):
        return self.__wd

    def change_curr_dir(self, path):
        is_absolute = path[0] == Parameters.path_sep
        path = path.strip('"' + Parameters.path_sep)

        if is_absolute:
            new_path = Parameters.path_sep + path
        else:
            if self.__wd[-1] != Parameters.path_sep:
                self.__wd += Parameters.path_sep
            new_path = self.__wd + path

        new_path = self.__validate_path(new_path)
        if new_path:
            self.__wd = new_path
        else:
            handle_error("Path {} does not exist.".format(new_path))

    @staticmethod
    def __validate_path(path):
        print("Validating path {}".format(path))
        return path

    @staticmethod
    def send_command(command, args):
        # Send command to the namenode and receive an answer
        print(Colors.colored("Command: {}".format(command), Colors.OKBLUE))
        print(Colors.colored("Args: {}".format(args)))

        return 0
