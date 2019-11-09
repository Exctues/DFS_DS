import os
import socket
from threading import Thread
from codes import Codes
from storage.commands import CommandHandler
from constants import Constants


class NamenodeListener(Thread):
    def __init__(self, sock: socket.socket):
        super().__init__(daemon=True)
        self.sock = sock
        self.error_code = 0

    def run(self):
        # wait for a code
        code = self.sock.recv(4).decode()
        self.sock.send('ok'.encode('utf-8'))
        # dispatch the code
        if code == 1:  # make_file (not dir)
            full_path = self.sock.recv(1024).decode()
            CommandHandler.handle_make_file(full_path)
        elif code == 4:  # rm
            full_path = self.sock.recv(1024).decode()
            CommandHandler.handle_rmdir(full_path)
        elif code == 6:  # copy
            source = self.sock.recv(1024).decode()
            self.sock.send('ok'.encode('utf-8'))
            destination = self.sock.recv(1024).decode()
            CommandHandler.handle_copy(source, destination)
        elif code == 7:  # move
            source = self.sock.recv(1024).decode()
            self.sock.send('ok'.encode('utf-8'))
            destination = self.sock.recv(1024).decode()
            CommandHandler.handle_move(source, destination)
        elif code == 9:  # mkdir
            full_path = self.sock.recv(1024).decode()
            CommandHandler.handle_mkdir(full_path)
        else:
            print("Namenode: no command correspond to code", code)
            error_code = -1

        # self.sock.send(str(self.error_code).encode('utf-8'))
        self.sock.close()


class ClientListener(Thread):
    def __init__(self, sock: socket.socket):
        super().__init__(daemon=True)
        self.sock = sock
        self.error_code = 0

    def _close(self):
        self.sock.close()

    def run(self):
        code = self.sock.recv(4).decode()
        self.sock.send('ok'.encode('utf-8'))
        # dispatch the code
        if code == 2:  # print
            full_path = self.sock.recv(1024).decode()
            CommandHandler.handle_print(full_path)
        elif code == 3:  # upload
            full_path = self.sock.recv(1024).decode()
            CommandHandler.handle_print(full_path)

        # self.sock.send(str(self.error_code).encode('utf-8'))
        self.sock.close()


def init_sync():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((Constants.NAMENODE_IP, Constants.NEW_NODES_PORT))
    to_sync = sock.recv(1024).decode()


def main():
    init_sync()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', Constants.STORAGE_PORT))
    sock.listen()
    while True:
        sck, addr = sock.accept()
        print("Accepted address:", addr)
        if addr == Constants.NAMENODE_IP:
            print("This is Namenode connection")
            NamenodeListener(sck).start()
        else:
            print("This is Client connection")
            ClientListener(sck).start()


def fly():
    init_sync()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    NamenodeListener(sock).start()


if __name__ == '__main__':
    fly()
