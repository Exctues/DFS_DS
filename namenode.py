# N cmd data
import os
import time
import socket
import sys
from namenode.handlers import Handlers
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

            con.close()

    new_nodes_listener = Thread(target=new_nodes_listener_thread)
    new_nodes_listener.start()



#filesystem = Tree()
# Heartbeat().start()
