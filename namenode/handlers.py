# OUT
import socket
from threading import Thread
from codes import Codes


class Handlers:

    @staticmethod
    def send_args(ip, port, cmd, arg1='', arg2=''):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))

        sock.send(cmd.encode('utf-8'))
        # acknowledge
        a = sock.recv(1024).decode('utf-8')
        sock.send(arg1.encode('utf-8'))
        if arg2 != '':
            # acknowledge
            a = sock.recv(1024).decode('utf-8')
            sock.send(arg2.encode('utf-8'))

        sock.close()

    @staticmethod
    def multicast(ips, port, cmd, arg1='', arg2=''):
        for ip in ips:
            thread = Thread(target=Handlers.send_args, args=[ip, port, cmd, arg1, arg2])
            thread.start()

    @staticmethod
    def make_file():
        pass

    @staticmethod
    def init():
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
        # TODO: куда и кого послать
        Handlers.send_args()

    @staticmethod
    def mkdir(ips, port, tree, filepath):
        Handlers.multicast(ips, port, getattr(Codes, 'make_dir'), filepath)
        # TODO: add filesize to tree.insert and to send
        tree.insert(filepath)

    @staticmethod
    def rmdir(ips, port, tree, filepath):
        Handlers.multicast(ips, port, getattr(Codes, 'rmdir'), filepath)
        # TODO: add filesize to tree.insert and to send
        tree.insert(filepath)


# proveryat' chto source suchshestvuet v dereve