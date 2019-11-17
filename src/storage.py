import os
import socket

from threading import Thread
from utils.codes import Codes
from storage.commands import CommandHandler
from utils.constants import Constants
from utils import logger


class NamenodeListener(Thread):
    def __init__(self, sock: socket.socket):
        super().__init__(daemon=True)
        self.sock = sock

    def run(self):
        code = int(self.sock.recv(4).decode('utf-8'))
        self.sock.send('ok'.encode('utf-8'))
        logger.print_debug_info(code)

        if code == Codes.make_file:
            full_path = self.sock.recv(1024).decode('utf-8')
            CommandHandler.handle_make_file(full_path)
        elif code == Codes.rm:
            full_path = self.sock.recv(1024).decode('utf-8')
            CommandHandler.handle_rm(full_path)
        elif code == Codes.copy:
            source = self.sock.recv(1024).decode('utf-8')
            self.sock.send('ok'.encode('utf-8'))
            destination = self.sock.recv(1024).decode('utf-8')
            CommandHandler.handle_copy(source, destination)
        elif code == Codes.move:
            source = self.sock.recv(1024).decode('utf-8')
            self.sock.send('ok'.encode('utf-8'))
            destination = self.sock.recv(1024).decode('utf-8')
            CommandHandler.handle_move(source, destination)
        elif code == Codes.make_dir:
            full_path = self.sock.recv(1024).decode('utf-8')
            CommandHandler.handle_mkdir(full_path)
        elif code == Codes.rmdir:
            full_path = self.sock.recv(1024).decode('utf-8')
            CommandHandler.handle_rmdir(full_path)
        elif code == Codes.init:
            if os.path.exists(Constants.STORAGE_PATH):
                os.removedirs(Constants.STORAGE_PATH)
            # then create this dir empty
            os.makedirs(Constants.STORAGE_PATH)
        else:
            print("NamenodeListener: no command correspond to code", code)

        self.sock.close()


class ClientListener(Thread):
    def __init__(self, sock: socket.socket, address: tuple):
        super().__init__(daemon=True)
        self.sock = sock
        self.address = address

    def run(self):
        code = self.sock.recv(1024).decode('utf-8')
        self.sock.send('ok'.encode('utf-8'))
        logger.print_debug_info(code)

        if code == Codes.print:
            full_path = self.sock.recv(1024).decode('utf-8')
            CommandHandler.handle_print_to(self.sock, full_path)
        elif code == Codes.upload:
            full_path, need_distribute = self.sock.recv(1024).decode('utf-8').split(';')
            self.sock.send('ok'.encode('utf-8'))
            CommandHandler.handle_upload_from(self.sock, full_path)
            if need_distribute == '1':
                # Important to decide whether to close socket right now or after distribution.
                # Performance or consistency? Consistency!
                CommandHandler.distribute(full_path)
        elif code == Codes.download_all:
            CommandHandler.handle_download_all(self.address)
        else:
            print("ClientListener: no command correspond to code", code)
        # regarding shutdown:
        # Shut down one or both halves of the connection.
        # If how is SHUT_RD,   further receives are disallowed.
        # If how is SHUT_WR,   further sends are disallowed.
        # If how is SHUT_RDWR, further sends and receives are disallowed.
        self.sock.close()


@logger.log
def get_sync_storage_ip():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((Constants.NAMENODE_IP, Constants.NEW_NODES_PORT))
    sock.send(str(Codes.init_new_storage).encode('utf-8'))
    sock.recv(1024)
    sock.send(socket.gethostname().encode('utf-8'))
    to_sync = sock.recv(1024).decode('utf-8')
    sock.close()
    return to_sync


@logger.log
def notify_i_clear():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((Constants.NAMENODE_IP, Constants.NEW_NODES_PORT))
    sock.send(str(Codes.i_clear).encode('utf-8'))
    sock.recv(1024)
    sock.send(socket.gethostname().encode('utf-8'))
    sock.close()


@logger.log
def remove_and_create_storage_dirs():
    if os.path.exists(Constants.STORAGE_PATH):
        os.removedirs(Constants.STORAGE_PATH)
        logger.print_debug_info(Constants.STORAGE_PATH, "removed")
        # then create this dir empty
    os.makedirs(Constants.STORAGE_PATH, exist_ok=True)
    logger.print_debug_info(Constants.STORAGE_PATH, "(re)created")


@logger.log
def init_sync():
    # First we delete everything we have
    # because we don't resurrect old nodes.
    remove_and_create_storage_dirs()

    storage_ip = get_sync_storage_ip()
    logger.print_debug_info("storage_ip", storage_ip)
    if storage_ip == '-1':
        return
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # connect and ask for all files
    sock.connect((storage_ip, Constants.STORAGE_PORT))
    sock.send(str(Codes.download_all).encode('utf-8'))

    # From this point we are going to receive a lot mkdir, and upload requests
    # from another storage and in this socket we are just waiting
    # When we receive ack then we are consistent with storage with 'storage_ip'
    sock.recv(1024)
    # Notify we are clear
    notify_i_clear()

    sock.close()


@logger.log
def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', Constants.STORAGE_PORT))
    sock.listen()
    init_sync()
    while True:
        logger.print_debug_info("Wait on accept.")
        sck, addr = sock.accept()
        if addr[0] == Constants.NAMENODE_IP:
            logger.print_debug_info("This is Namenode connection", addr)
            NamenodeListener(sck).start()
        else:
            logger.print_debug_info("This is Client(or Storage) connection", addr)
            ClientListener(sck, addr).start()


if __name__ == '__main__':
    main()
