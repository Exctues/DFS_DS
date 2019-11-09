# N cmd data
import os
import random
import time
import socket
import sys
# from namenode.handlers import Handlers
from namenode.tree import FSTree
from constants import Constants
from codes import Codes
from threading import Thread, Lock


class Nodes:
    def __init__(self, ips=None):
        self.nodes = set(ips) if ips else set()
        self.lock = Lock()


# all storage nodes
storage_nodes = Nodes()


def send_args(ip, port, cmd, arg1='', arg2=''):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))

    sock.send(cmd.encode('utf-8'))
    if arg1 != '':
        # acknowledge
        a = sock.recv(1024).decode('utf-8')
        sock.send(arg1.encode('utf-8'))
        if arg2 != '':
            # acknowledge
            a = sock.recv(1024).decode('utf-8')
            sock.send(arg2.encode('utf-8'))

    sock.close()


def multicast(cmd, arg1='', arg2=''):
    """
    threaded multicast to all storage servers
    :param cmd:
    :param arg1:
    :param arg2:
    :return:
    """
    for ip in storage_nodes.nodes:
        thread = Thread(target=send_args, args=[ip, Constants.STORAGE_PORT, cmd, arg1, arg2])
        thread.start()


def randomip():
    return random.sample(storage_nodes, 1).encode('utf-8')


# thread that pings nodes and modify storage_nodes
def ping():
    def ping_thread():
        while True:
            for ip in storage_nodes.nodes.copy():
                response = os.system("ping -c 1 " + ip)
                if response != 0:
                    with storage_nodes.lock:
                        storage_nodes.nodes.discard(ip)
            time.sleep(30)

    heartbeat = Thread(target=ping_thread)
    heartbeat.start()


# thread that listens and add new storage nodes
def new_nodes_listener():
    def new_nodes_listener_thread():
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        soc.bind(('', Constants.NEW_NODES_PORT))
        soc.listen()
        while True:
            con, addr = soc.accept()
            with storage_nodes.lock:
                storage_nodes.nodes.add(addr)
            # TODO: переделать аддр на аддр(0) потому что аддр это тупл
            # TODO: сторейдж стучиться два раза, второй раз когда она все скопировала и готова для отдачи
            con.send(random.sample(storage_nodes, 1).encode('utf-8'))
            # ack
            # a = con.recv(1024).decode('utf-8')

            con.close()

    new_nodes_listener = Thread(target=new_nodes_listener_thread)
    new_nodes_listener.start()


tree = FSTree()

# Main thread
while True:
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    soc.bind(('', Constants.CLIENT_TO_NAMENODE))
    soc.listen()
    while True:
        con, addr = soc.accept()  # addr is a tuple

        code = int(con.recv(1024).decode('utf-8'))
        con.send('ok'.encode('utf-8'))

        if code == 0:  # init
            tree.wipe()
            multicast(getattr(Codes, 'init'), '0')

        elif code == 1:  # make_file (not dir)
            filepath = con.recv(1024).decode('utf-8')
            # Handlers.make_file(storage_nodes.nodes, tree, full_path)
            tree.insert(filepath, 0)
            multicast(getattr(Codes, 'make_dir'), filepath)

        elif code == 2:  # print # download
            source = con.recv(1024).decode('utf-8')
            # Handlers.print(addr[0], addr[1], random.sample(storage_nodes, 1).encode('utf-8'))
            randomip = random.sample(storage_nodes, 1).encode('utf-8')
            con.send(randomip().encode('utf-8'))

        elif code == 3:  # upload
            filename = con.recv(1024).decode('utf-8')
            con.send('ok'.encode('utf-8'))
            size = int(con.recv(1024).decode('utf-8'))
            # Handlers.upload(addr[0], addr[1], tree, size, filename, random.sample(storage_nodes, 1).encode('utf-8'))
            tree.insert(filename, size)
            con.send(randomip().encode('utf-8'))

        elif code == 4:  # rm
            filename = con.recv(1024).decode('utf-8')
            tree.remove(filename)
            # Handlers.rm(storage_nodes.nodes, tree, full_path)
            multicast(getattr(Codes, 'rm'), filename)

        elif code == 5:  # info
            filename = con.recv(1024).decode('utf-8')
            node = tree.find_node(filename)
            con.send(node.name.encode('utf-8'))
            # ack
            a = con.recv(1024).decode('utf-8')
            con.send(str(node.size).encode('utf-8'))

        elif code == 6:  # copy
            source = con.recv(1024).decode('utf-8')
            con.send('ok'.encode('utf-8'))
            destination = con.recv(1024).decode('utf-8')
            tree.insert(destination)
            multicast(getattr(Codes, 'copy'), source, destination)

        elif code == 7:  # move
            source = con.recv(1024).decode('utf-8')
            con.send('ok'.encode('utf-8'))
            destination = con.recv(1024).decode('utf-8')
            tree.remove(source)
            tree.insert(destination)
            multicast(getattr(Codes, 'move'), source, destination)

        elif code == 8:  # ls
            source = con.recv(1024).decode('utf-8')
            children = tree.find_node(source).children
            child_str = ';'.join(children)
            con.send(child_str.encode('utf-8'))

        elif code == 9:  # make_dir
            filepath = con.recv(1024).decode('utf-8')
            tree.insert(filepath)
            multicast(getattr(Codes, 'make_dir'), filepath)

        elif code == 10:  # rmdir
            filepath = con.recv(1024).decode('utf-8')
            tree.remove(filepath)
            multicast(getattr(Codes, 'rmdir'), filepath)

        con.close()

# TODO: доделать дерево ремув и вайп эсс
