from client.utils import *
from constants import Constants
from codes import Codes

import os
import socket


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

    def resolve_path(self, path):
        if path[0] == '/':
            return path
        else:
            return f"/{self.get_curr_dir().strip('/')}/{path.strip('/')}"

    @staticmethod
    def __validate_path(path):
        print("Validating path {}".format(path))
        return path

    @staticmethod
    def handle_upload(command, args):
        assert len(args) == 2
        if not os.path.isfile(args[0]):
            handle_error("Incorrect host path specified!")

        with open(args[0], 'rb') as host_file:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((Constants.NAMENODE_IP, Constants.CLIENT_TO_NAMENODE))

                sock.send(command.code.encode('utf-8'))
                sock.recv(1024)

                sock.send(args[1])
                sock.recv(1024)

                size = os.path.getsize(args[0])
                sock.send(str(size).encode('utf-8'))
                ip = sock.recv(1024).decode('utf-8')

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((ip, Constants.STORAGE_PORT))
                sock.send(args[1])
                data = host_file.read(1024)

                while data:
                    sock.send(data)
                    sock.recv(1)
                    data = host_file.read(1024)

    @staticmethod
    def handle_print(command, source):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((Constants.NAMENODE_IP, Constants.CLIENT_TO_NAMENODE))

            sock.send(command.code.encode('utf-8'))
            ip = sock.recv(1024).decode('utf-8')

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((ip, Constants.STORAGE_PORT))
            sock.send(source)
            res = ""

            while data:
                data = sock.recv(1024)
                if data:
                    res += data.decode('utf-8')
                    sock.send('1'.encode('utf-8'))
                else:
                    return

    @staticmethod
    def send_command(command, args):
        # Send command to the namenode and receive an answer
        # print(Colors.colored("Command: {}".format(command), Colors.OKBLUE))
        # print(Colors.colored("Args: {}".format(args)))
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((Constants.NAMENODE_IP, Constants.CLIENT_TO_NAMENODE))
            sock.send(command.code.encode('utf-8'))

            for arg in args:
                sock.recv(1024)
                sock.send(arg.encode('utf-8'))

        return 0

    @staticmethod
    def n_args_handler(command, args):
        for arg in args:
            Session.send_command(command, arg)
