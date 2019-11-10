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
        self.__wd = path

    def resolve_partial_path(self, path, new_length=1):
        """
        For commands like make_file and make_dir.
        Build the full path and resolve, but validate (check is exists) only the portion of it
        The portion to not validate (leave out of validation) is specified by new_length parameter

        :param path:        path to resolve (build and validate)
        :param new_length:  number of path entries (separated by separator) to leave out of validation
        :return:            correct path validated on namenode, if the path was valid
                            None, is the path could not be found
        """
        res = self.__build_path(path)
        path = res.split(Parameters.sep)
        part_path = path[:-new_length]
        new_path = path[-new_length:]
        part_path = Parameters.sep + Parameters.sep.join(part_path)
        part_path = self.validate_path(part_path).strip(Parameters.sep)

        if part_path is None:
            return None

        res = f"{Parameters.sep}{Parameters.sep.join(part_path)}" \
              f"{Parameters.sep}{Parameters.sep.join(new_path)}"

        return res

    def resolve_full_path(self, path):
        res = self.__build_path(path)
        res = self.validate_path(res)
        return res

    def __build_path(self, path):
        path = path.strip('"')

        if path[0] == Parameters.sep:
            res = path
        else:
            curr_dir = self.get_curr_dir().strip(Parameters.sep)

            res = f"{Parameters.sep}{curr_dir}" \
                  f"{Parameters.sep}{path.strip(Parameters.sep)}"

        return res

    @staticmethod
    def validate_path(path):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.send(str(Codes.validate_path).encode('utf-8'))
            is_valid = int(sock.recv(1024).decode('utf-8'))
            if is_valid:
                true_path = sock.recv(1024).decode('utf-8')
            else:
                handle_error("Path {} is invalid!".format(path))
                true_path = None

        return true_path

    @staticmethod
    def handle_info(command, args):
        sock = Session.send_command(command, args, close_socket=False)
        filename = sock.recv(1024).decode('utf-8')
        # ack
        sock.send('ok'.encode('utf-8'))
        size = sock.recv(1024).decode('utf-8')
        print_response("{}\t{}".format(filename, size))

        sock.shutdown(0)

    @staticmethod
    def handle_ls(command, args):
        sock = Session.send_command(command, args, close_socket=False)
        l = sock.recv(1024).decode('utf-8')
        l = l.split(Parameters.path_sep)
        print_response('\n'.join(l))
        sock.shutdown(0)

    @staticmethod
    def handle_upload(command, args):
        assert len(args) == 2
        if not os.path.isfile(args[0]):
            handle_error("Incorrect host path specified!")

        with open(args[0], 'rb') as host_file:
            size = str(os.path.getsize(args[0]))

            sock = Session.send_command(command, (args[1], size), close_socket=False)
            ip = sock.recv(1024).decode('utf-8')
            sock.shutdown(0)

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
        sock = Session.send_command(command, (source,), close_socket=False)
        ip = sock.recv(1024).decode('utf-8')
        sock.shutdown(0)

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
    def send_command(command, args, close_socket=True):
        # Send command to the namenode, send arguments and return socket

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((Constants.NAMENODE_IP, Constants.CLIENT_TO_NAMENODE))
        sock.send(command.code.encode('utf-8'))

        for arg in args:
            sock.recv(1024)
            sock.send(arg.encode('utf-8'))

        if close_socket:
            sock.shutdown(0)
            return True

        return sock
