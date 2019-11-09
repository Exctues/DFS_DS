# N cmd data
import os
import random
import time
import socket
import sys
from namenode.handlers import Handlers
from namenode.tree import FSTree
from constants import Constants

from threading import Thread, Lock

class Nodes:
    def __init__(self, ips=None):
        self.nodes = set(ips) if ips else set()
        self.lock = Lock()

# all storage nodes
storage_nodes = Nodes()

# thread that pings nodes and modify storage_nodes
def ping():
    def ping_thread():
        while True:
            for ip in storage_nodes.nodes:
                response = os.system("ping -c 1 " + ip)
                if response != 0:
                    with storage_nodes.lock:
                        storage_nodes.nodes.remove(ip)
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

            con.send(random.sample(storage_nodes, 1).encode('utf-8'))
            # ack
            # a = con.recv(1024).decode('utf-8')

            con.close()

    new_nodes_listener = Thread(target=new_nodes_listener_thread)
    new_nodes_listener.start()

tree = FSTree()

while True:
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    soc.bind(('', Constants.CLIENT_TO_NAMENODE))
    soc.listen()
    while True:
        con, addr = soc.accept()

        cmd = con.recv(1024).decode('utf-8')


        con.close()
