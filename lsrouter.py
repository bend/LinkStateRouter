import socket
import logging
from lsrouter_table import *
from lsrouter_listener import *
from lsrouter_sender import *
from lsrouter_buffer import *
from lsrouter_hello import *
from type import *
import sys

class LsRouter:
    send_queue = []
    ack_queue = []


    def __init__(self, filename, hello_interval, lsp_interval):
        # Create logger
        logging.basicConfig(format='%(asctime)s %(levelname)s\t%(message)s', level = logging.DEBUG)
        # Create Socket
        self.router_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Read conf
        self.routing_table = LsRouterTable(filename)
        logging.info("Binding socket on "+self.routing_table.router_port)
        # Bind socket
        self.router_socket.bind(("127.0.0.1", int(self.routing_table.router_port)))
        self.hello_interval = hello_interval
        self.lsp_interval = lsp_interval
        # Create buffer
        self.buffer = LsRouterBuffer()
        # Start listener thread
        self.listener = LsRouterListener(self.router_socket,self.routing_table, self.buffer)
        self.listener.start()
        # Start hello and lsp thread
        self.hello_sender = LsRouterHello(self.router_socket, self.routing_table, self.hello_interval, self.lsp_interval, self.buffer)
        self.hello_sender.start()

        # Start sender thread
        self.sender = LsRouterSender(self.router_socket, self.routing_table, self.buffer)
        self.sender.start()
        
        while(1):
            command = sys.stdin.readline()
            cmd = command.split(' ')
            print('[',cmd[0].strip(),']')
            if cmd[0].strip() == "send":
                if len(cmd) >= 3:
                    self.buffer.add_send(["DATA", self.routing_table.router_name, cmd[1], cmd[2]])
                    print("Message sent")
                else:
                    print("Command usage : send [ROUTER NAME] [message]")
        


a = LsRouter(sys.argv[1], 5, 60)
