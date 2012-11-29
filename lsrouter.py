import socket
from type import *

class LsRouter:

    self.router_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.routingTable

    def send(self, type, sender, reveiver, message = None):
        if type == Type.HELLO:
            pass
        elif type == Type.LSP:
            pass
        elif type == Type.LSACK:
            pass
        elif type == Type.DATA:
            pass
        else:
            print("Wrong Type")



