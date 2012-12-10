#!/usr/bin/env python
import socket
import logging
from lsrouter_table import *
from lsrouter_listener import *
from lsrouter_sender import *
from lsrouter_buffer import *
from lsrouter_hello import *
from type import *
import sys
import getopt

class LsRouter:
    send_queue = []
    ack_queue = []


    def __init__(self, filename, hello_interval, lsp_interval, log_level):
        # Create logger
        logging.basicConfig(format='%(asctime)s %(levelname)s\t%(message)s', level = log_level)
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
            if cmd[0].strip() == "send":
                if len(cmd) >= 3:
                    self.buffer.add_send(["DATA", self.routing_table.router_name, cmd[1], cmd[2]])
                    print("Message sent")
                else:
                    print("Command usage : send [ROUTER NAME] [message]")
            elif cmd[0].strip() == "print":
                print(self.routing_table)
        


#############################################################################################################

def print_help():
    print("Usage : lsrouter [options] -c|--config filename")
    print("Options:")
    print("-h|--hello-interval interval\t\t: Hello packets interval")
    print("-l|--lsp-interval interval\t\t: LSP packets interval")
    print("-v|--log-level level\t\t\t: Log level (debug, info, warning, error)")



options, remainder = getopt.getopt(sys.argv[1:], 'v:l:h:c:', ['log-level=','lsp-interval=','hello-interval='])


log_level = logging.INFO
hello_interval = 5
lsp_interval = 30
config = None

for opt, arg in options:
    if opt in ('-v','--log-level'):
        if arg == "debug":
            log_level=logging.DEBUG
        if arg == "info":
            log_level = logging.INFO
        if arg == "warning":
            log_level = logging.WARNING
        if arg == "error":
            log_level = logging.CRITICAL
    elif opt in ('-l','--lsp-interval'):
        lsp_interval = int(arg)
    elif opt in ('-h', '--hello-interval'):
        hello_interval = int(arg)
    elif opt in ('-c', '--config'):
        config = arg
    else:
        print("help")

if config is None:
    print("Missing configuration file")
    print_help()
    exit()

a = LsRouter(config, hello_interval, lsp_interval, log_level)
