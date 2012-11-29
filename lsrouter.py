import socket
from lsparser import *
from type import *

class LsRouter:

    def __init__(self, filename):
        self.router_socket = socket.socketpair(socket.AF_INET, socket.SOCK_DGRAM)
        self.config = LsParser(filename)
        self.router_socket.bind("127.0.0.1", config.router_port)

    def start(self):
        while 1:
            data,addr = self.router_socket.recvfrom(1024)
            if not data:
                sys.stderr.write("Error listening")
            else:
                print(data)
                print(addr)
            

    def send(self, type, sender, receiver, message = None):
        if type == Type.HELLO:
            pass
        elif type == Type.LSP:
            pass
        elif type == Type.LSACK:
            pass
        elif type == Type.DATA:
            pass
        else:
            sys.stderr.write("Wrong Type")



a = LsRouter("config")
