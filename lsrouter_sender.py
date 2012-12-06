import threading
import time
import logging
import math
from type import *

class LsRouterSender(threading.Thread):

    def __init__(self, router_socket, routing_table, buffer ):
        threading.Thread.__init__(self)
        self.router_socket = router_socket
        self.routing_table = routing_table
        self.send = True
        self.buffer = buffer

    def run(self):
        logging.info("Starting Sender thread.")
        routing_table = self.routing_table.neighbours
        router_name = self.routing_table.router_name
        while(self.send):
            tosend = self.buffer.pop_send()
            self.handle_send(tosend)

    def handle_send(self, tokens):
        if tokens[0] == Type.DATA:
            self.send_data(tokens[1], tokens[2], tokens[3])
        elif tokens[0] == Type.LSACK:
            self.send_lsack(tokens[1], tokens[2])
        elif tokens[0] == Type.LSP:
            self.send_lsp(tokens)

    def send_lsack(self, sender, seq_nb):
        """ Send LSACK to the sender of the LSP """
        tosend = 'LSACK '+ sender + ' '+seq_nb
        if sender in self.routing_table.neighbours:
            neighbour = self.routing_table.neighbours[sender]
            addr = (neighbour[0], int(neighbour[1]))
            tosend = tosend.encode('UTF-8')
            self.router_socket.sendto(tosend,addr)
            logging.debug("LSACK sent to "+sender+" seq# "+seq_nb)
        else:
            logging.error("Unintended LSP received from "+sender," seq#: "+ seq_nb)

    def send_lsp(self, tokens):
        """ Forwards lsp to all neighbours"""
        tosend = " "
        tosend=tosend.join(tokens)
        tosend = tosend.encode('UTF-8')
        for key,value in self.routing_table.neighbours.items():
            if value[4]:
                addr = (value[0], int(value[1]))
                self.router_socket.sendto(tosend,addr)
                logging.debug("LSP sent. seq#: "+tokens[2])

    def send_data(self, sender, receiver, msg):
        tosend = 'DATA '+sender+' '+receiver+' '+msg
        if receiver in self.routing_table.table:
            # Get addr
            via = self.routing_table.table[receiver]
            if via[0] in self.routing_table.neighbours:
                neighbour = self.routing_table.neighbours[via[0]]
                addr = (neighbour[0], int(neighbour[1]))
                tosend = tosend.encode('UTF-8')
                self.router_socket.sendto(tosend, addr)
            else:
                logging.error("Via is not a neighbour "+via[0])
        else:
            logging.error("Unknown host "+receiver)



