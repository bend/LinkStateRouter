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
        """ Reads data from the buffer and send it over the network"""
        logging.info("Starting Sender thread.")
        routing_table = self.routing_table.neighbours
        router_name = self.routing_table.router_name
        while(self.send):
            tosend = self.buffer.pop_send() # Blocking call if no elements in Buffer
            self.handle_send(tosend)

    def handle_send(self, tokens):
        """ Handle the sending of different tokens"""
        if tokens[0] == Type.DATA:
            self.send_data(tokens[1], tokens[2], tokens[3])
        elif tokens[0] == Type.LSACK:
            self.send_lsack(tokens)
        elif tokens[0] == Type.LSP:
            self.send_lsp(tokens)
        elif tokens[0] == Type.LSP_ONE:
            self.send_lsp_one(tokens)
        elif tokens[0] == Type.HELLO:
            self.send_hello(tokens)

    def send_lsack(self, tokens):
        """ Send LSACK to the sender of the LSP """
        try:
            tosend = " "
            tosend = tosend.join(tokens[0:3])
            addr = tokens[3]
            tosend = tosend.encode('ASCII')
            self.router_socket.sendto(tosend,addr)
            logging.debug("LSACK sent seq# "+str(tokens[2]))
        except socket.error:
            logging.error("Could not send, socket error")

    def send_lsp(self, tokens):
        """ Forwards lsp to all neighbours"""
        try:
            tosend = " "
            tosend=tosend.join(tokens)
            tosend = tosend.encode('ASCII')
            for key,value in self.routing_table.neighbours.items():
                if value[Field.ACTIVE]:
                    addr = (value[Field.HOST], int(value[Field.PORT]))
                    self.router_socket.sendto(tosend,addr)
                    logging.debug("LSP sent. seq#: "+tokens[2]+" to "+key)
                    value[Field.LSPLIST][tokens[2]]=[time.time(), tokens]
            self.routing_table.lsp_timestamp=time.time() #Update LSP timestamp
        except socket.error:
            logging.error("Could not send, socket error")
    
    def send_lsp_one(self, tokens):
        """ Send LSP to one neighbour """
        try:
            tosend = " "
            tosend=tosend.join(tokens[2:]) # Don't take the 2 first fields
            tosend = tosend.encode('ASCII')
            value = self.routing_table.neighbours[tokens[1]]
            addr = (value[Field.HOST], int(value[Field.PORT]))
            self.router_socket.sendto(tosend,addr)
            logging.debug("LSP resent. seq#: "+tokens[4]+" to "+tokens[1])
            # Update timestamp of LSP
            value[Field.LSPLIST][tokens[4]][0] = time.time()
            self.routing_table.lsp_timestamp=time.time() #Update time
        except socket.error:
            logging.error("Could not send, socket error")
        

    def send_data(self, sender, receiver, msg):
        """ Forward DATA packets"""
        try:
            tosend = 'DATA '+sender+' '+receiver+' '+msg
            if receiver in self.routing_table.table:
                # Get addr
                via = self.routing_table.table[receiver]
                if via in self.routing_table.neighbours:
                    neighbour = self.routing_table.neighbours[via]
                    addr = (neighbour[Field.HOST], int(neighbour[Field.PORT]))
                    tosend = tosend.encode('ASCII')
                    self.router_socket.sendto(tosend, addr)
                else:
                    logging.error("Via is not a neighbour "+via)
            else:
                logging.error("Unknown host "+receiver)
        except socket.error:
            logging.error("Could not send, socket error")

    def send_hello(self, tokens):
        """ Sends the hello packet"""
        try:
            addr=tokens[3]
            """ Sends HELLO Packet to addr"""
            logging.debug("Sending HELLO to "+tokens[2])
            tosend = " "
            tosend = tosend.join(tokens[0:3])
            tosend = tosend.encode('ASCII')
            # Add LSP to send buffer
            self.router_socket.sendto(tosend,addr)
        except socket.error:
            logging.error("Could not send, socket error")




