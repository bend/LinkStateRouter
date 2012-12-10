import threading
import time
import logging
import math
from type import *
from graph import graph
from dijkstra import *

class LsRouterHello(threading.Thread):
    """ Sends regular HELLO and LSP packet
        Resends LSP if not acked """

    def __init__(self, router_socket, routing_table, hello_interval, lsp_interval, buffer):
        threading.Thread.__init__(self)
        self.router_socket = router_socket
        self.routing_table = routing_table
        self.send = True
        self.hello_interval = hello_interval
        self.lsp_interval = lsp_interval
        self.buffer = buffer


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
        # Init phase, send hello to all neighbours
        init = True

        while(self.send):
            for key, value in routing_table.items():
                if value[Field.ACTIVE] or init:
                    if value[Field.TSH] < time.time() - self.hello_interval*3:
                        # Link is dead
                        value[Field.ACTIVE] = False
                        # Remove not acked list
                        value[Field.LSPLIST] = {}
                        logging.warning("Link "+key+" is inactive")
                        if self.routing_table.graph.has_edge((self.routing_table.router_name, key)):
                            self.routing_table.graph.del_edge((self.routing_table.router_name, key))
                        self.routing_table.table = get_next_step(self.routing_table.graph, \
                                                                 self.routing_table.router_name)
                        self.routing_table.update()
                        # Send LSP to neighbours because new dead link detected
                        self.send_lsp()
                    if last_hello_timestamp < time.time() - self.hello_interval:
                        # Send HELLO because timeout
                        self.send_hello(router_name, key, (value[0], int(value[1])))
                        hello_update = True
                        # Browse all LSP that are not acked for this user and check is timout expired (5s)                       
                        lsp_no_acked = value[Field.LSPLIST]
                        for lspseq, lsp_to in lsp_no_acked.items():
                            if lsp_to[0] < time.time() - 5:
                                # LSP not acket in more than 5 sec
                                self.send_lsp_one(key, lsp_to[1])
            init = False # Init phase completed
            # Update timestamp
            if hello_update:
                last_hello_timestamp = time.time()
                hello_update = False

            if self.routing_table.lsp_timestamp < time.time() - self.lsp_interval:
                print('max delay')
                # Send LSP because MAX_LSP_DELAY reached
                self.send_lsp()
            time.sleep(1)
    
    def send_hello(self, sender, receiver,addr):
        """ Sends HELLO Packet to addr"""
        msg = 'HELLO '+sender+' '+receiver
        tokens = msg.split(' ')
        tokens.append(addr)
        # Add LSP to send buffer
        self.buffer.add_send(tokens)

    def send_lsp_one(self, receiver, lsp):
        """ Send LSP to only one receiver"""
        tokens = []
        tokens.append(Type.LSP_ONE)
        tokens.append(receiver)
        tokens+=lsp
        # Add to the send buffer
        self.buffer.add_send(tokens)

    def send_lsp(self):
        """ Sends LSP to all neighbours"""
        sender = self.routing_table.router_name
        msg = 'LSP '+sender+' '+str(self.routing_table.seq_nb)+' '
        neighbours_table = self.routing_table.neighbours
        # Build LSP Packet
        for key, value in neighbours_table.items():
            if value[Field.ACTIVE]:
                msg+=key+' '+value[2]+' '

        self.routing_table.seq_nb = (self.routing_table.seq_nb+1)%100
        self.buffer.add_send(msg.split(' '))
        
