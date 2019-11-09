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

    def run(self):
        # wait for a code
        code = int(self.sock.recv(4).decode('utf-8'))
        self.sock.send('ok'.encode('utf-8'))
        # dispatch the code
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
        else:
            print("NamenodeListener: no command correspond to code", code)

        # TODO if doesn't work change to shutdown()
        self.sock.close()


class ClientListener(Thread):
    def __init__(self, sock: socket.socket):
        super().__init__(daemon=True)
        self.sock = sock

    def _close(self):
        self.sock.close()

    def run(self):
        code = self.sock.recv(4).decode('utf-8')
        self.sock.send('ok'.encode('utf-8'))
        # dispatch the code
        if code == Codes.print:
            full_path = self.sock.recv(1024).decode('utf-8')
            CommandHandler.handle_print_to(self.sock, full_path)
        elif code == Codes.upload:
            full_path = self.sock.recv(1024).decode('utf-8')
            CommandHandler.handle_upload_from(self.sock, full_path)
        elif code == Codes.download_all:
            pass
        else:
            print("ClientListener: no command correspond to code", code)

        # TODO if doesn't work change to shutdown()
        self.sock.close()


def get_sync_storage_ip():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((Constants.NAMENODE_IP, Constants.NEW_NODES_PORT))
    to_sync = sock.recv(1024).decode('utf-8')
    sock.close()
    return to_sync


def init_sync():
    storage_ip = get_sync_storage_ip()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((storage_ip, Constants.STORAGE_PORT))
    # TODO: gather all files from another storage

    # TODO: Also notify namenode that this node is clear now


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


if __name__ == '__main__':
    main()
