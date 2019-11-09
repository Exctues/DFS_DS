import os
import shutil
import socket


class CommandHandler:
    # IN
    @staticmethod
    def handle_copy(source, destination):
        shutil.copy(source, destination)

    @staticmethod
    def handle_move(source, destination):
        shutil.move(source, destination)

    @staticmethod
    def handle_rm(full_path):
        os.remove(full_path)

    @staticmethod
    def handle_upload(socket: socket.socket, full_path):
        # code for receiving file from a client
        with open(full_path, 'wb+') as file:
            while data:
                data = socket.recv(1024)
                if data:
                    file.write(data)
                    socket.send('1'.encode('utf-8'))
                else:
                    return

    @staticmethod
    def handle_print(socket: socket.socket, full_path):
        # code for sending file to a client
        with open(full_path, 'rb+') as file:
            data = file.read(1024)
            while data:
                socket.send(data)
                socket.recv(1)
                data = file.read(1024)

    @staticmethod
    def handle_mkdir(full_path):
        os.makedirs(full_path, exist_ok=True)

    @staticmethod
    def handle_make_file(full_path):
        # wb+ creates a file
        with open(full_path, "wb+"):
            pass

    @staticmethod
    def handle_rmdir(full_path):
        os.rmdir(full_path)
