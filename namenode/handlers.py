# # OUT
# import socket
# from threading import Thread
# from codes import Codes
# from constants import Constants
#
# class Handlers:
#
#     @staticmethod
#     def send_args(ip, port, cmd, arg1='', arg2=''):
#         sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         sock.connect((ip, port))
#
#         sock.send(cmd.encode('utf-8'))
#         # acknowledge
#         a = sock.recv(1024).decode('utf-8')
#         sock.send(arg1.encode('utf-8'))
#         if arg2 != '':
#             # acknowledge
#             a = sock.recv(1024).decode('utf-8')
#             sock.send(arg2.encode('utf-8'))
#
#         sock.close()
#
#     @staticmethod
#     def multicast(ips, port, cmd, arg1='', arg2=''):
#         for ip in ips:
#             thread = Thread(target=Handlers.send_args, args=[ip, port, cmd, arg1, arg2])
#             thread.start()
#
#     @staticmethod
#     def init(tree):
#         # remove all filesystem
#         tree.wipe()
#
#     @staticmethod
#     def make_file(ips, tree, filepath):
#         tree.insert(filepath, 0)
#         Handlers.multicast(ips, Constants.STORAGE_PORT, getattr(Codes, 'make_dir'), filepath)
#
#     @staticmethod
#     def print(ip, port, arg): # download
#         Handlers.send_args(ip, port, getattr(Codes, 'print'), arg)
#
#     @staticmethod
#     def upload(ip, port, tree, size, filepath, randomip):
#         tree.insert(filepath, size)
#         Handlers.send_args(ip, port, getattr(Codes, 'print'), randomip)
#
#     @staticmethod
#     def rm(ips, tree, filepath):
#         tree.remove(filepath)
#         Handlers.multicast(ips, Constants.STORAGE_PORT, getattr(Codes, 'rm'), filepath)
#
#     @staticmethod
#     def info():
#         pass
#
#     @staticmethod
#     def copy():
#         pass
#
#     @staticmethod
#     def move(tree, filepath1, filepath2):
#         tree.remove(filepath1)
#         tree.insert(filepath2)
#
#     @staticmethod
#     def ls():
#         Handlers.send_args()
#
#     @staticmethod
#     def mkdir(ips, port, tree, filepath):
#         Handlers.multicast(ips, port, getattr(Codes, 'make_dir'), filepath)
#         tree.insert(filepath)
#
#     @staticmethod
#     def rmdir(ips, port, tree, filepath):
#         Handlers.multicast(ips, port, getattr(Codes, 'rmdir'), filepath)
#         tree.insert(filepath)
#
#
# # proveryat' chto source suchshestvuet v dereve