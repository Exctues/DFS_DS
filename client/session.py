from constants import Constants
from codes import Codes
import parameters
import logger

import os
import socket


class Session:
    def __init__(self, interactive=True):
        self.__wd = "/"
        self.interactive = interactive

    @logger.log
    def print_curr_dir(self, *args):
        logger.print_info(self.get_curr_dir())

    def get_curr_dir(self):
        return self.__wd

    def change_curr_dir(self, path):
        self.__wd = path

    @logger.log
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
        logger.print_debug_info("built partial path:", res)
        path = res.split(parameters.sep)
        path = list(filter(lambda path: path != '', path))
        # if len(path) <= 1:
            # return path
        part_path = path[:-new_length]
        new_path = path[-new_length:]
        part_path = parameters.sep + parameters.sep.join(part_path)
        part_path = self.validate_path(part_path)
        logger.print_debug_info("Received from validate_path:", part_path)
        if part_path:
            part_path = part_path.strip(parameters.sep)
        else:
            logger.handle_error("Path is not valid")
            return None

        res = "{}{}{}{}".format(parameters.sep, parameters.sep.join(part_path), parameters.sep, 
                                parameters.sep.join(new_path))

        logger.print_debug_info("{} -> {}".format(parameters.sep + parameters.sep.join(path), res))

        return res

    @logger.log
    def resolve_full_path(self, path):
        res = self.__build_path(path)
        res = self.validate_path(res)
        if parameters.verbose:
            logger.print_debug_info("{} -> {}".format(path, res))

        return res

    def __build_path(self, path):
        path = path.strip('"')

        if path[0] == parameters.sep:
            res = path
        else:
            curr_dir = self.get_curr_dir().strip(parameters.sep)

            res = "{}{}{}{}".format(parameters.sep, curr_dir, parameters.sep, path.strip(parameters.sep))
        
        return res

    @staticmethod
    @logger.log
    def validate_path(path):
        if not path or path == parameters.sep:
            # root
            return True

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((Constants.NAMENODE_IP, Constants.CLIENT_TO_NAMENODE))
            sock.send(str(Codes.validate_path).encode('utf-8'))
            sock.recv(1024)
            sock.send(path.encode('utf-8'))
            is_valid = (sock.recv(1024).decode('utf-8'))
            logger.print_debug_info("RECEIVED", is_valid)
            try:
                is_valid = int(is_valid)
            except:
                logger.print_debug_info("Couldn't cast to int")
                return False

            if is_valid:
                logger.print_debug_info("Valid")
                sock.send('ok'.encode('utf-8'))
                true_path = sock.recv(1024).decode('utf-8')
            else:
                logger.print_debug_info("Invalid")
                logger.handle_error("Path {} is invalid!".format(path))
                true_path = None

        return true_path

    @staticmethod
    @logger.log
    def handle_info(command, args):
        sock = Session.send_command(command, args, close_socket=False)
        filename = sock.recv(1024).decode('utf-8')
        # ack
        sock.send('ok'.encode('utf-8'))
        size = sock.recv(1024).decode('utf-8')
        logger.print_info("{}\t{} bytes".format(filename, size))

        # sock.shutdown(0)
        sock.close()

    @staticmethod
    @logger.log
    def handle_ls(command, args):
        sock = Session.send_command(command, args, close_socket=False)
        l = sock.recv(1024).decode('utf-8')
        l = l.split(parameters.path_sep)
        logger.print_info('\n'.join(l))
        # sock.shutdown(0)
        sock.close()

    @staticmethod
    @logger.log
    def handle_upload(command, args):
        assert len(args) == 2
        if not os.path.isfile(args[0]):
            logger.handle_error("Incorrect host path specified!")
            return

        with open(args[0], 'rb') as host_file:
            size = str(os.path.getsize(args[0]))

            sock = Session.send_command(command, (args[1], size), close_socket=False)
            ip = sock.recv(1024).decode('utf-8')
            # sock.shutdown(0)
            sock.close()

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((ip, Constants.STORAGE_PORT))
                sock.send(args[1])
                sock.recv(1024)
                sock.send('1'.encode('utf-8'))
                data = host_file.read(1024)

                while data:
                    sock.send(data)
                    sock.recv(1)
                    data = host_file.read(1024)

                sock.close()
        
        logger.print_info(data)

    @staticmethod
    @logger.log
    def handle_print(command, source):
        sock = Session.send_command(command, (source,), close_socket=False)
        ip = sock.recv(1024).decode('utf-8')
        # sock.shutdown(0)
        sock.close()

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
        
        logger.print_info(data)

    @staticmethod
    @logger.log
    def send_command(command, args, close_socket=True):
        # Send command to the namenode, send arguments and return socket
        logger.print_debug_info("Send command invoked!")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((Constants.NAMENODE_IP, Constants.CLIENT_TO_NAMENODE))
        sock.send(str(command.code).encode('utf-8'))
        logger.print_debug_info("Sent command", command.name)

        for arg in args:
            sock.recv(1024)
            logger.print_debug_info("Received ack")
            sock.send(arg.encode('utf-8'))
            logger.print_debug_info("Sent arg", arg)

        if close_socket:
            # sock.shutdown(0)
            sock.close()
            return True

        return sock
