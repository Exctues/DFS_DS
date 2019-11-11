# N cmd data
import os
import random
import time
import socket
import sys
from namenode.tree import FSTree
from constants import Constants
from codes import Codes
from threading import Thread, Lock
import logger


class Nodes:
    def __init__(self, ips=None):
        self.nodes = set(ips) if ips else set()
        self.lock = Lock()


# all storage nodes
clean_nodes = Nodes()
dirty_nodes = Nodes()

@logger.log
def send_args(ip, port, cmd, arg1='', arg2=''):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))

    sock.send(cmd.encode('utf-8'))
    if arg1 != '':
        # acknowledge
        sock.recv(1024)
        sock.send(arg1.encode('utf-8'))
    if arg2 != '':
        # acknowledge
        sock.recv(1024)
        sock.send(arg2.encode('utf-8'))

    sock.shutdown(0)

@logger.log
def multicast(cmd, arg1='', arg2=''):
    """
    threaded multicast to all storage servers
    :param cmd:
    :param arg1:
    :param arg2:
    :return:
    """

    # wait for all the dirty nodes to become clean
    while len(dirty_nodes.nodes) > 0:
        pass

    for ip in clean_nodes.nodes:
        thread = Thread(target=send_args, args=[ip, Constants.STORAGE_PORT, cmd, arg1, arg2])
        thread.start()

@logger.log
def random_ip():
    return random.sample(clean_nodes.nodes, 1).encode('utf-8')


# thread that pings nodes and modify storage_nodes
@logger.log
def ping():
    def ping_thread():
        while True:
            for ip in clean_nodes.nodes.copy():
                response = os.system("ping -c 1 " + ip)
                if response != 0:
                    with clean_nodes.lock:
                        clean_nodes.nodes.discard(ip)
            time.sleep(30)

    heartbeat = Thread(target=ping_thread)
    heartbeat.start()


# thread that listens and add new storage nodes
@logger.log
def new_nodes_listener():
    def new_nodes_listener_thread():
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        soc.bind(('', Constants.NEW_NODES_PORT))
        soc.listen()
        while True:
            # get_all_storage_ips = 12
            # init_new_storage = 13
            # i_clear = 15

            con, addr = soc.accept()
            print('new connection')
            code = int(con.recv(1024).decode('utf-8'))

            if code == Codes.i_clear:
                dirty_nodes.nodes.discard(addr[0])
                clean_nodes.nodes.add(addr[0])

            elif code == Codes.init_new_storage:
                if len(clean_nodes.nodes) > 0:
                    dirty_nodes.nodes.add(addr[0])
                    con.send(random_ip().encode('utf-8'))
                else:
                    con.send('-1'.encode('utf-8'))
                    clean_nodes.nodes.add(addr[0])

            elif code == Codes.get_all_storage_ips:
                if len(clean_nodes.nodes) > 0:
                    con.send(';'.join(clean_nodes.nodes).encode('utf-8'))
                else:
                    con.send('-1'.encode('utf-8'))

            con.shutdown(0)

    new_nodes_listener = Thread(target=new_nodes_listener_thread)
    new_nodes_listener.start()

ping()
new_nodes_listener()

tree = FSTree()

# Main thread
while True:
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    soc.bind(('', Constants.CLIENT_TO_NAMENODE))
    soc.listen()
    while True:
        con, addr = soc.accept() # addr is a tuple

        code = int(con.recv(1024).decode('utf-8'))
        con.send('ok'.encode('utf-8'))

        if code == Codes.init: # init
            del tree
            tree = FSTree()
            multicast(Codes.init)

        elif code == Codes.make_file: # make_file (not dir)
            filepath = con.recv(1024).decode('utf-8')
            tree.insert(filepath, 0)
            multicast(Codes.make_file, filepath)

        elif code == Codes.print: # print # download
            source = con.recv(1024).decode('utf-8')
            con.send(random_ip().encode('utf-8'))

        elif code == Codes.upload: # upload
            filename = con.recv(1024).decode('utf-8')
            con.send('ok'.encode('utf-8'))
            size = int(con.recv(1024).decode('utf-8'))
            tree.insert(filename, size)
            con.send(random_ip().encode('utf-8'))

        elif code == Codes.rm: # rm
            filename = con.recv(1024).decode('utf-8')
            tree.remove(filename)
            multicast(Codes.rm, filename)

        elif code == Codes.info: # info
            filename = con.recv(1024).decode('utf-8')
            node = tree.find_node(filename)
            con.send(node.name.encode('utf-8'))
            # ack
            a = con.recv(1024).decode('utf-8')
            con.send(str(node.size).encode('utf-8'))

        elif code == Codes.copy: # copy
            source = con.recv(1024).decode('utf-8')
            con.send('ok'.encode('utf-8'))
            destination = con.recv(1024).decode('utf-8')
            tree.insert(destination)
            multicast(Codes.copy, source, destination)

        elif code == Codes.move: # move
            source = con.recv(1024).decode('utf-8')
            con.send('ok'.encode('utf-8'))
            destination = con.recv(1024).decode('utf-8')
            tree.remove(source)
            tree.insert(destination)
            multicast(Codes.move, source, destination)

        elif code == Codes.ls: # ls
            source = con.recv(1024).decode('utf-8')
            children = tree.find_node(source).get_children()
            child_str = ';'.join(children)
            con.send(child_str.encode('utf-8'))

        elif code == Codes.make_dir: # make_dir
            filepath = con.recv(1024).decode('utf-8')
            tree.insert(filepath)
            multicast(Codes.make_dir, filepath)

        elif code == Codes.rmdir: # rmdir
            filepath = con.recv(1024).decode('utf-8')
            tree.remove(filepath)
            multicast(Codes.rmdir, filepath)

        elif code == Codes.validate_path: # validate_path
            filepath = con.recv(1024).decode('utf-8')
            path = tree.find_node(filepath)
            if path is not None:
                con.send(str(1).encode('utf-8'))
                # ack
                con.recv(1024)
                con.send(path.get_path().encode('utf-8'))
            else:
                con.send(str(0).encode('utf-8'))
        con.shutdown(0)
