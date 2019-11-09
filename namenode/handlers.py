# OUT
import socket
from threading import Thread
from codes import Codes

class Handlers:

    @staticmethod
    def send_args(ip, port, command):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        sock.send(command.encode('utf-8'))
        sock.close()

    @staticmethod
    def multicast(ips, port, command):
        for ip in ips:
            thread = Thread(target=Handlers.send_args, args=[ip, port, command])
            thread.start()

    @staticmethod
    def make_file():
        pass

    @staticmethod
    def print():
        pass

    @staticmethod
    def upload(filepath, size):
        # tree.insert(filepath, size)
        # send_random_ip(client)
        pass

    @staticmethod
    def rm():
        pass

    @staticmethod
    def info():
        pass

    @staticmethod
    def copy():
        pass

    @staticmethod
    def move(tree, filepath1, filepath2):
        tree.remove(filepath1)
        tree.insert(filepath2)

    @staticmethod
    def ls():
        #TODO: куда и кого послать
        Handlers.send_args()

    @staticmethod
    def mkdir(ips, port, tree, filepath):
        Handlers.multicast(ips, port, 'N'+getattr(Codes,'make_dir')+filepath)
        # TODO: add filesize to tree.insert and to send
        tree.insert(filepath)

    @staticmethod
    def rmdir(ips, port, tree, filepath):
        Handlers.multicast(ips, port, 'N' + getattr(Codes, 'rmdir') + filepath)
        # TODO: add filesize to tree.insert and to send
        tree.insert(filepath)
