import os
import shutil
import socket
from constants import Constants
from codes import Codes
import logger


# full_path is expected to start with '/', not '/var/dfs_storage/
# real_path is '/var/dfs_storage/...'
class CommandHandler:
    @staticmethod
    @logger.log
    def handle_copy(source, destination):
        shutil.copy(os.path.join(Constants.STORAGE_PATH, source),
                    os.path.join(Constants.STORAGE_PATH, destination))

    @staticmethod
    @logger.log
    def handle_move(source, destination):
        shutil.move(os.path.join(Constants.STORAGE_PATH, source),
                    os.path.join(Constants.STORAGE_PATH, destination))

    @staticmethod
    @logger.log
    def handle_rm(full_path):
        os.remove(os.path.join(Constants.STORAGE_PATH, full_path))

    @staticmethod
    @logger.log
    def handle_upload_from(socket: socket.socket, full_path):
        # receiving file from a client
        with open(os.path.join(Constants.STORAGE_PATH, full_path), 'wb+') as file:
            while data:
                data = socket.recv(1024)
                if data:
                    file.write(data)
                    socket.send('1'.encode('utf-8'))
                else:
                    return

    @staticmethod
    @logger.log
    def handle_print_to(socket: socket.socket, full_path):
        # sending file to a client
        with open(os.path.join(Constants.STORAGE_PATH, full_path), 'rb') as file:
            data = file.read(1024)
            while data:
                socket.send(data)
                socket.recv(1)
                data = file.read(1024)

    @staticmethod
    @logger.log
    def handle_download_all(address: tuple):
        """address is (host, port) tuple
           We do separate request for each make_dir & upload request
           for simplicity of code.
        """

        def ask(code, full_path):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(address)
            sock.send(str(code).encode('utf-8'))
            sock.recv(1024)  # ack
            if code == Codes.upload:
                # we need off distribution on upload
                sock.send(full_path + ' 0')
                sock.recv(1024)
                CommandHandler.handle_print_to(sock, full_path)
            else:
                sock.send(full_path)
            sock.shutdown(1)

        # for all files
        for dir_name, subdir_list, file_list in os.walk(Constants.STORAGE_PATH):
            ask(Codes.make_dir, dir_name)
            for file in file_list:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect(address)
                full_path = os.path.join(os.path.abspath(dir_name), file)[len(Constants.STORAGE_PATH):]
                ask(Codes.upload, full_path)

    @staticmethod
    @logger.log
    def distribute(full_path: str):
        """Distributing a file which we just uploaded from a client"""
        # real_path = os.path.join(Constants.STORAGE_PATH, full_path)
        # ask namenode for all storage's ips
        storages_ip = CommandHandler._get_all_storages_ip()
        # send file to everybody
        for ip in storages_ip:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((ip, Constants.STORAGE_PORT))
            # Check if another storage doesn't have a file
            if not CommandHandler._has_file(sock, full_path):
                print("Distributing", full_path)
                sock.send(full_path.encode('utf-8'))
                sock.recv(1024)
                CommandHandler.handle_print_to(sock, full_path)
            sock.shutdown(1)

    @staticmethod
    @logger.log
    def handle_mkdir(full_path):
        os.makedirs(os.path.join(Constants.STORAGE_PATH, full_path), exist_ok=True)

    @staticmethod
    @logger.log
    def handle_make_file(full_path):
        with open(os.path.join(Constants.STORAGE_PATH, full_path), "wb+"):
            return

    @staticmethod
    @logger.log
    def handle_rmdir(full_path):
        os.rmdir(full_path)

    @staticmethod
    @logger.log
    def _get_all_storages_ip():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((Constants.NAMENODE_IP, Constants.NEW_NODES_PORT))
        ips = sock.recv(1024).decode('utf-8').strip().split(" ")
        sock.shutdown(1)
        return ips

    @staticmethod
    def _has_file(sock: socket.socket, full_path) -> bool:
        # We simply replace all files without assuming there is a file with such filename.
        return False
