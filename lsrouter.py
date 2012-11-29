import socket
from lsparser import *
from type import *

class LsRouter:

    
    def __init__():
        self.router_socket = socket.socketpair(socket.AF_INET, socket.SOCK_DGRAM)
        self.config = 

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



