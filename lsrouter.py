import socket
from Type import *

class LsRouter:

    self.s = socket.socketpair(socket.AF_INET, socket.SOCK_DGRAM)

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



