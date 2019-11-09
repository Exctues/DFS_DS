import os
import shutil


class CommandHandler:
    # IN
    @staticmethod
    def handle_copy(source, destination):
        shutil.copy(source, destination)

    @staticmethod
    def handle_move(source, destination):
        shutil.move(source, destination)

    @staticmethod
    def handle_upload(full_path):
        # code for receiving file from a client

        pass

    @staticmethod
    def handle_print(full_path):
        # code for sending file to a client
        pass

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
        os.removedirs(full_path)
