import socket
import logging
from lsparser import *
from lsrouter_listener import *
from lsrouter_hello import *
from type import *

class LsRouter:

    def __init__(self, filename, interval):
        logging.basicConfig(filename= "lsrouter.log", level = logging.DEBUG)
        self.router_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Read conf
        self.config = LsParser(filename)
        logging.info("Binding socket on "+self.config.router_port)
        # Bind socket
        self.router_socket.bind(("127.0.0.1", int(self.config.router_port)))
        # Start listener thread
        self.listener = LsRouterListener(self.router_socket,self.config)
        self.listener.start()

        self.hello_sender = LsRouterHello(self.router_socket, self.config, interval)
        self.hello_sender.start()


    def send(self, type,addr, sender, receiver, message = None):
        if type == Type.LSP:
            pass
        elif type == Type.LSACK:
            pass
        elif type == Type.DATA:
            pass
        else:
            logging.error("Message if from wrong Type")



a = LsRouter("config", 5)
