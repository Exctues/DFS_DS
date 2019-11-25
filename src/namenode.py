# N cmd data
import time

from namenode.tree import FSTree
from utils.constants import Constants
from utils.codes import Codes
from utils import logger

import random
import socket

from threading import Thread, Lock


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

    sock.send(str(cmd).encode('utf-8'))
    if arg1 != '':
        # acknowledge
        sock.recv(1024)
        sock.send(arg1.encode('utf-8'))
    if arg2 != '':
        # acknowledge
        sock.recv(1024)
        sock.send(arg2.encode('utf-8'))

    sock.close()


@logger.log
def multicast(cmd, arg1='', arg2=''):
    """
    threaded multicast to all storage servers
    :param cmd:
    :param arg1:
    :param arg2:
    :return:
    """
    logger.print_debug_info("code", cmd)
    logger.print_debug_info("dirty_nodes:", dirty_nodes)
    logger.print_debug_info("clean_nodes:", clean_nodes)

    # wait for all the dirty nodes to become clean
    while len(dirty_nodes.nodes) > 0:
        pass

    for ip in clean_nodes.nodes:
        thread = Thread(target=send_args, args=[ip, Constants.NAMENODE_TO_STORAGE, cmd, arg1, arg2])
        thread.start()


@logger.log
def random_address():
    return random.sample(clean_nodes.nodes, 1)[0]


# thread that pings nodes and modify storage_nodes.nodes
@logger.log
def ping():
    def ping_thread():
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(Constants.PING_TIMEOUT)
        while True:
            time.sleep(10)
            for ip in clean_nodes.nodes.copy():
                sock.sendto('ping'.encode('utf-8'), (ip, Constants.STORAGE_PING))
                try:
                    sock.recvfrom(1024)
                except socket.timeout:
                    with clean_nodes.lock:
                        clean_nodes.nodes.discard(ip)
                    logger.print_debug_info('timeout storagenode', ip)
                except Exception as e:
                    logger.print_debug_info('exception during ping' + str(e))

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
            code = int(con.recv(1024).decode('utf-8'))
            # ack
            con.send('ack'.encode('utf-8'))
            storagename = con.recv(1024).decode('utf-8')

            if code == Codes.i_clear:
                logger.print_debug_info("Node {} says it's clean".format(storagename))
                dirty_nodes.nodes.discard(storagename)
                clean_nodes.nodes.add(storagename)

            elif code == Codes.init_new_storage:
                if len(clean_nodes.nodes) > 0:
                    dirty_nodes.nodes.add(storagename)
                    copy_from = random_address()
                    con.send(copy_from.encode('utf-8'))
                    logger.print_debug_info("New storage node {} connected "
                                            "and will copy from {}".format(storagename, copy_from))
                else:
                    # sanity check
                    assert len(dirty_nodes.nodes) == 0
                    con.send('-1'.encode('utf-8'))
                    clean_nodes.nodes.add(storagename)
                    logger.print_debug_info("New storage node {} connected, system init".format(storagename))

            elif code == Codes.get_all_storage_ips:
                if len(clean_nodes.nodes) > 0:
                    res = ';'.join(clean_nodes.nodes)
                else:
                    res = '-1'

                con.send(res.encode('utf-8'))
                logger.print_debug_info("Node {} requested ip list. Sending {}".format(storagename, res))

            con.close()

    new_nodes_listener = Thread(target=new_nodes_listener_thread)
    new_nodes_listener.start()


new_nodes_listener()
ping()

tree = FSTree()

# Main thread
while True:
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    soc.bind(('', Constants.CLIENT_TO_NAMENODE))
    soc.listen()
    while True:
        logger.print_debug_info("Waiting for a new client connection")
        con, addr = soc.accept()  # addr is a tuple
        logger.print_debug_info('New client connection')

        code = int(con.recv(1024).decode('utf-8'))
        logger.print_debug_info('Received code ' + str(code))

        con.send('ok'.encode('utf-8'))

        if code == Codes.init:  # init
            del tree
            tree = FSTree()
            multicast(Codes.init)
            logger.print_debug_info('init success')

        elif code == Codes.make_file:  # make_file (not dir)
            filepath = con.recv(1024).decode('utf-8')
            tree.insert(filepath, 0)
            multicast(Codes.make_file, filepath)
            logger.print_debug_info('makefile success')

        elif code == Codes.print:  # download
            source = con.recv(1024).decode('utf-8')
            while len(dirty_nodes.nodes) > 0:
                pass

            storage_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            storage_sock.connect((random_address(), Constants.NAMENODE_TO_STORAGE))
            storage_sock.send(str(Codes.print).encode('utf-8'))
            storage_sock.recv(1024)
            storage_sock.send(source.encode('utf-8'))

            data = storage_sock.recv(1024)
            while data:
                if data:
                    con.send(data)
                data = storage_sock.recv(1024)
            storage_sock.close()

        elif code == Codes.upload:  # upload
            filename = con.recv(1024).decode('utf-8')
            con.send('ok'.encode('utf-8'))
            size = int(con.recv(1024).decode('utf-8'))
            con.send('ok'.encode('utf-8'))

            while len(dirty_nodes.nodes) > 0:
                pass

            storage_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            storage_sock.connect((random_address(), Constants.NAMENODE_TO_STORAGE))
            storage_sock.send(str(Codes.upload).encode('utf-8'))
            storage_sock.recv(1024)
            storage_sock.send(filename.encode('utf-8'))
            storage_sock.recv(1024)

            data = con.recv(1024)
            while data:
                if data:
                    storage_sock.send(data)
                data = con.recv(1024)
            tree.insert(filename, size=size)
            storage_sock.close()

        elif code == Codes.rm:  # rm
            filename = con.recv(1024).decode('utf-8')
            tree.remove(filename)
            multicast(Codes.rm, filename)

        elif code == Codes.info:  # info
            filename = con.recv(1024).decode('utf-8')
            node = tree.find_node(filename)
            con.send(node.name.encode('utf-8'))
            # ack
            a = con.recv(1024).decode('utf-8')
            con.send(str(node.size).encode('utf-8'))

        elif code == Codes.copy:  # copy
            source = con.recv(1024).decode('utf-8')
            con.send('ok'.encode('utf-8'))
            destination = con.recv(1024).decode('utf-8')
            node = tree.find_node(source)
            tree.insert(destination, node.size)
            multicast(Codes.copy, source, destination)

        elif code == Codes.move:  # move
            source = con.recv(1024).decode('utf-8')
            con.send('ok'.encode('utf-8'))
            destination = con.recv(1024).decode('utf-8')
            size = tree.find_node(source).size
            tree.remove(source)
            tree.insert(destination, size)
            multicast(Codes.move, source, destination)

        elif code == Codes.ls:  # ls
            source = con.recv(1024).decode('utf-8')
            node = tree.find_node(source)
            children = node.get_children()

            if not node.is_dir:
                child_str = children
            else:
                child_str = ';'.join(children)
            con.send(child_str.encode('utf-8'))

        elif code == Codes.make_dir:  # make_dir
            filepath = con.recv(1024).decode('utf-8')
            logger.print_debug_info(filepath)
            tree.insert(filepath)
            multicast(Codes.make_dir, filepath)

        elif code == Codes.rmdir:  # rmdir
            filepath = con.recv(1024).decode('utf-8')
            tree.remove(filepath)
            multicast(Codes.rmdir, filepath)

        elif code == Codes.validate_path:  # validate_path
            filepath = con.recv(1024).decode('utf-8')
            path = tree.find_node(filepath)
            if path is not None:
                con.send(str(1).encode('utf-8'))
                logger.print_debug_info('validate path send 1 ')
                # ack
                con.recv(1024)
                res = path.get_path()
                con.send(res.encode('utf-8'))
                logger.print_debug_info(f'validate {path} send {res}')
            else:
                con.send(str(0).encode('utf-8'))
                logger.print_debug_info('validate path send 0')
        elif code == Codes.is_dir:
            filepath = con.recv(1024).decode('utf-8')
            res = tree.find_node(filepath).is_dir

            con.send(str(int(res)).encode('utf-8'))
            logger.print_debug_info("is_dir send {}".format(int(res)))

        con.close()
