import socket
import logging
from lsrouter_neighbours import *
from lsrouter_listener import *
from lsrouter_hello import *
from type import *

class LsRouter:

    def __init__(self, filename, interval):
        logging.basicConfig(filename= "lsrouter.log", level = logging.DEBUG)
        self.router_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Read conf
        self.neighbours = LsRouterNeighbours(filename)
        logging.info("Binding socket on "+self.neighbours.router_port)
        # Bind socket
        self.router_socket.bind(("127.0.0.1", int(self.neighbours.router_port)))
        # Start listener thread
        self.listener = LsRouterListener(self.router_socket,self.neighbours)
        self.listener.start()

        # Start hello thread
        self.hello_sender = LsRouterHello(self.router_socket, self.neighbours, interval)
        self.hello_sender.start()


    def send(self, type,addr, sender, receiver, message = None):
        if type == Type.LSP:
            # LSP [SENDER] [Seq#] [List of adj active links]
            pass
        elif type == Type.LSACK:
            # LSACK [SENDER] [Seq#]
            pass
        elif type == Type.DATA:
            # DATA [SENDER] [RECEIVER] [MSG]
            pass
        else:
            logging.error("Message if from wrong Type")



a = LsRouter(sys.argv[1], 5)
