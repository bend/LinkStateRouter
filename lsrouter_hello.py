import threading
import time
import logging
import math
from type import *
from graph import graph
from dijkstra import *

class LsRouterHello(threading.Thread):

    def __init__(self, router_socket, routing_table, hello_interval, lsp_interval, buffer):
        threading.Thread.__init__(self)
        self.router_socket = router_socket
        self.routing_table = routing_table
        self.send = True
        self.hello_interval = hello_interval
        self.lsp_interval = lsp_interval
        self.buffer = buffer
        self.seq_nb = 0


    def run(self):
        """ Sends regular HELLO and LSP packets
            Detects the dead links
            Resends a LSP Packet if not acked
        """
        logging.info("Starting HELLO thread. Interval "+str(self.hello_interval))
        routing_table = self.routing_table.neighbours
        router_name = self.routing_table.router_name
        last_hello_timestamp = 0
        hello_update = False
        while(self.send):
            for key, value in routing_table.items():
                if value[Field.ACTIVE]:
                    if value[Field.TSH] < time.time() - self.hello_interval*3:
                        # Link is dead
                        value[Field.ACTIVE] = False
                        logging.warning("Link "+key+" is inactive")
                        self.routing_table.graph.del_edge((self.routing_table.router_name, key))
                        if not self.routing_table.graph.neighbors(key):
                            self.routing_table.graph.del_node(key)
                        print(self.routing_table.graph)
                        if self.routing_table.graph.neighbors(self.routing_table.router_name):
                            self.routing_table.table = get_next_step(self.routing_table.graph, \
                                                                 self.routing_table.router_name)
                        else:
                            self.routing_table.table = {}
                        # TODO remove the edge from the graph and recompute the shortest path
                        # Send LSP to neighbours because new dead link detected
                        self.send_lsp()
                    if last_hello_timestamp < time.time() - self.hello_interval:
                        # Send HELLO because timeout
                        self.send_hello(router_name, key, (value[0], int(value[1])))
                        hello_update = True
                    if not value[Field.ACKR] and value[Field.TLSP]<time.time() - 5:
                        # LSP not acked within the 5 sec. Resend it
                        self.send_lsp_one(key)

            # Update timestamp
            if hello_update:
                last_hello_timestamp = time.time()
                hello_update = False

            if self.routing_table.lsp_timestamp < time.time() - self.lsp_interval:
                # Send LSP because MAX_LSP_DELAY reached
                self.send_lsp()
            time.sleep(1)
    
    def send_hello(self, sender, receiver,addr):
        try:
            """ Sends HELLO Packet to addr"""
            logging.debug("Sending HELLO to "+receiver)
            msg = 'HELLO '+sender+' '+receiver
            msg = msg.encode('ASCII')
            self.router_socket.sendto(msg,addr)
        except socket.error:
            logging.error("Could not send, socket error")



    def send_lsp_one(self, receiver):
        """ Send LSP to only one receiver"""
        try:
            sender = self.routing_table.router_name
            msg = 'LSP '+sender+' '+str(self.seq_nb)+' '
            neighbours_table = self.routing_table.neighbours
            # Build LSP Packet
            for key, value in neighbours_table.items():
                if value[Field.ACTIVE]:
                    msg+=key+' '+value[Field.COST]+' '

            msg = msg.encode('ASCII')
            value = neighbours_table[receiver]
            if value[Field.ACTIVE]:
                neighbours_table[receiver][5] = False # Ack not received for this lsp
                logging.debug("Re-sending LSP to "+key+" seq # "+str(self.seq_nb))
                self.router_socket.sendto(msg,(value[Field.HOST], int(value[Field.PORT])))
            self.routing_table.lsp_timestamp=time.time() #send time of the lsp
            value[Field.TLSP] = time.time()
            value[Field.LSPNB] = self.seq_nb
            self.seq_nb= (self.seq_nb+1)%100
        except socket.error:
            logging.error("Could not send, socket error")

    def send_lsp(self):
        """ Sends LSP to all neighbours"""
        try:
            sender = self.routing_table.router_name
            msg = 'LSP '+sender+' '+str(self.seq_nb)+' '
            neighbours_table = self.routing_table.neighbours
            # Build LSP Packet
            for key, value in neighbours_table.items():
                if value[Field.ACTIVE]:
                    msg+=key+' '+value[2]+' '
            msg = msg.encode('ASCII')
            
            for key,value in neighbours_table.items():
                if value[Field.ACTIVE]:
                    neighbours_table[key][5] = False # Ack not received for this lsp
                    logging.debug("Sending LSP to "+key+" seq # "+str(self.seq_nb))
                    self.router_socket.sendto(msg,(value[0], int(value[1])))
                    value[Field.TLSP] = time.time()
                    value[Field.LSPNB] = self.seq_nb
            self.routing_table.lsp_timestamp=time.time() #send time of the lsp
            self.seq_nb= (self.seq_nb+1)%100
        except socket.error:
            logging.error("Could not send, socket error")

