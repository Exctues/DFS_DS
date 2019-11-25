import os
import shutil
import socket
from utils.constants import Constants
from utils.codes import Codes
from utils import logger


# full_path is expected to start with '/', not '/var/dfs_storage/
# real_path is '/var/dfs_storage/...'
class CommandHandler:
    @staticmethod
    @logger.log
    def handle_copy(source: str, destination: str):
        # to properly join
        source = source.strip(os.sep)
        destination = destination.strip(os.sep)

        shutil.copy(os.path.join(Constants.STORAGE_PATH, source),
                    os.path.join(Constants.STORAGE_PATH, destination))

    @staticmethod
    @logger.log
    def handle_move(source: str, destination: str):
        source = source.strip(os.sep)
        destination = destination.strip(os.sep)

        shutil.move(os.path.join(Constants.STORAGE_PATH, source),
                    os.path.join(Constants.STORAGE_PATH, destination))

    @staticmethod
    @logger.log
    def handle_rm(full_path: str):
        # to properly join
        full_path = full_path.strip(os.sep)

        os.remove(os.path.join(Constants.STORAGE_PATH, full_path))

    @staticmethod
    @logger.log
    def handle_upload_from(socket: socket.socket, full_path: str):
        # to properly join
        full_path = full_path.strip(os.sep)
        # receiving file from a client
        logger.print_debug_info("Receiving", full_path)
        with open(os.path.join(Constants.STORAGE_PATH, full_path), 'wb+') as file:
            data = socket.recv(1024)
            while data:
                if data:
                    file.write(data)
                else:
                    return
                data = socket.recv(1024)

    @staticmethod
    @logger.log
    def handle_print_to(socket: socket.socket, full_path: str):
        # to properly join
        full_path = full_path.strip(os.sep)
        # sending file to a client
        logger.print_debug_info("Sending", full_path)
        with open(os.path.join(Constants.STORAGE_PATH, full_path), 'rb') as file:
            data = file.read(1024)
            while data:
                socket.send(data)
                data = file.read(1024)

    @staticmethod
    @logger.log
    def handle_download_all(ip: tuple):
        """address is (host, port) tuple
           We do separate request for each make_dir & upload request
           for simplicity of code.
        """

        @logger.log
        def ask(code, full_path: str):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((ip, Constants.STORAGE_TO_STORAGE))
            sock.send(str(code).encode('utf-8'))
            sock.recv(1024)  # ack
            if code == Codes.upload:
                # we need off distribution on upload
                sock.send(full_path.encode('utf-8'))
                sock.recv(1024)
                CommandHandler.handle_print_to(sock, full_path)
            else:
                sock.send(full_path.encode('utf-8'))
            sock.close()

        home_path_length = len(Constants.STORAGE_PATH) + 1
        # print("home_path_length", home_path_length)
        # for all files
        for dir_name, subdir_list, file_list in os.walk(Constants.STORAGE_PATH):
            ask(Codes.make_dir, dir_name)

            # print("not processed", dir_name)
            dir_name = dir_name[home_path_length:]
            # print("processed", dir_name)
            if len(dir_name) > 0:
                # dir_name = os.path.join(*dir_name)
                logger.print_debug_info("replicate dir {}".format(dir_name))
                # print("dir_name is", dir_name)
                ask(Codes.make_dir, dir_name)
            else:
                dir_name = ''

            for file in file_list:
                logger.print_debug_info("downloading all: current file is", file)
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((ip, Constants.STORAGE_TO_STORAGE))
                full_path = os.path.join(dir_name, file)
                # print("fullpath is ", full_path)
                ask(Codes.upload, full_path)

    @staticmethod
    @logger.log
    def distribute(full_path: str):
        """Distributing a file which we just uploaded from a client"""
        # real_path = os.path.join(Constants.STORAGE_PATH, full_path)
        # ask namenode for all storage's ips
        storages_ip = CommandHandler._get_all_storages_ip()
        # send file to everybody
        if storages_ip is None:
            return

        for ip in storages_ip:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((ip, Constants.STORAGE_TO_STORAGE))
            # Check if another storage doesn't have a file
            sock.send(str(Codes.upload).encode('utf-8'))
            sock.recv(1024)
            if not CommandHandler._has_file(sock, full_path):
                logger.print_debug_info("Distributing", full_path)
                sock.send(full_path.encode('utf-8'))
                sock.recv(1024)
                CommandHandler.handle_print_to(sock, full_path)
            sock.close()

    @staticmethod
    @logger.log
    def handle_mkdir(full_path: str):
        # to properly join
        full_path = full_path.strip(os.sep)
        full_path = os.path.join(Constants.STORAGE_PATH, full_path)
        os.makedirs(full_path, exist_ok=True)
        if os.path.exists(full_path):
            return True

        logger.handle_error("Could not create path {}".format(full_path))
        return False
        # os.system("mkdir -p {}".format(os.path.join(Constants.STORAGE_PATH, full_path)))

    @staticmethod
    @logger.log
    def handle_make_file(full_path: str):
        # to properly join
        full_path = full_path.strip(os.sep)
        with open(os.path.join(Constants.STORAGE_PATH, full_path), "wb+"):
            logger.print_debug_info(os.path.join(
                Constants.STORAGE_PATH, full_path))
            return

    @staticmethod
    @logger.log
    def handle_rmdir(full_path: str):
        # to properly join
        full_path = full_path.strip(os.sep)
        full_path = os.path.join(Constants.STORAGE_PATH, full_path)
        shutil.rmtree(full_path)

    @staticmethod
    @logger.log
    def _get_all_storages_ip():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((Constants.NAMENODE_ADDRESS, Constants.NEW_NODES_PORT))
        sock.send(str(Codes.get_all_storage_ips).encode("utf-8"))
        sock.recv(1024)
        sock.send(socket.gethostname().encode('utf-8'))
        ips = sock.recv(1024).decode('utf-8').strip()
        sock.close()
        if ips == '-1':
            ips = None
        else:
            ips = ips.split(';')
            my_name = socket.gethostname()
            ips.remove(my_name)
        return ips

    @staticmethod
    def _has_file(sock: socket.socket, full_path) -> bool:
        # We simply replace all files without assuming there is a file with such filename.
        return False
