import threading
import logging
import time
from graph import graph
from dijkstra import *
from type import *


class LsRouterListener(threading.Thread):
    
    def __init__(self, router_socket, routing_table, buffer):
        threading.Thread.__init__(self)
        self.router_socket = router_socket
        self.routing_table = routing_table
        self.buffer = buffer
        self.listen = True
        self.routing_table.graph = self.create_graph()


    def create_graph(self):
        newgraph = graph()
        newgraph.add_node(self.routing_table.router_name)
        for key in self.routing_table.neighbours:
            newgraph.add_node(key)
            newgraph.add_edge((self.routing_table.router_name, key), \
                            int(self.routing_table.neighbours[key][2]))
        self.routing_table.table = get_next_step(newgraph, \
                                                 self.routing_table.router_name)
        self.routing_table.update()
        return newgraph

    def run(self):
        """ Listens and received packets from network"""
        logging.info("Starting listener thread")
        while self.listen:
            data,addr = self.router_socket.recvfrom(4096)
            if not data:
                logging.error("Error packet received from ", addr)
            else:
                self.package_handling(data, addr)

    def package_handling(self, packet, addr):
        """ Handles the received packets based on the type"""
        packet = packet.decode('ASCII')
        tokens = packet.split(' ')
        if tokens[0] == Type.HELLO:
            logging.debug("Received HELLO packet from " + tokens[1])
            if len(tokens) != 3:
                logging.error("Hello Packet error")
            sender = tokens[1]
            receiver = tokens[2]
            if receiver == self.routing_table.router_name:
                if sender in self.routing_table.neighbours:
                    self.routing_table.neighbours[sender][3] = time.time()
                    if not self.routing_table.neighbours[sender][4] :
                        # Link is now active
                        logging.info("New active link "+sender)
                        self.routing_table.neighbours[sender][4] = True
                        if not self.routing_table.graph.has_node(sender):
                            self.routing_table.graph.add_node(sender)
                        self.routing_table.graph.add_edge((self.routing_table.router_name, sender), \
                                          int(self.routing_table.neighbours[sender][2]))
                        self.routing_table.table = get_next_step(self.routing_table.graph, \
                                                                 self.routing_table.router_name)
                        self.routing_table.update()
                else:
                    logging.error("Received HELLO from unknown")
            else:
                logging.warning("Received HELLO not intended to router")
        elif tokens[0] == Type.LSP:
            self.handle_lsp(tokens)
        elif tokens[0] == Type.LSACK:
            self.handle_ack(tokens, addr)
        elif tokens[0] == Type.DATA:
            logging.debug("Received DATA packet from " + tokens[1])
            if len(tokens) != 4:
                logging.error("Hello Packet error")
            sender = tokens[1]
            receiver = tokens[2]
            msg = tokens[3]
            if receiver == self.routing_table.router_name:
                # Packet destination is self
                print("Message received: "+msg)
            else:
                self.buffer.add_send([Type.DATA,sender, receiver, msg]) 
        else:
            logging.error("Invalid packet received")


    def handle_lsp(self, tokens):
        """ Handle LSP packets. Discard if already received, 
        update routing table and forward if not already received"""
        sender = tokens[1]
        seq_nb = tokens[2]
        # Keep track of seq to avoid multiple receive and send of lsack
        if sender == self.routing_table.router_name:
            # Skip forwarded packet that was initited by this router
            logging.debug("Skipping LSP initiatest by us")
            return
        if sender in self.routing_table.seq:
            if self.routing_table.seq[sender] == seq_nb:
                # LSP already received, skip it
                logging.debug("Skipping already received LSP")
                self.buffer.add_send([Type.LSACK, sender, seq_nb])
                return
            else:
                # LSP not received already, update seq num
                logging.debug("Received LSP from "+sender+" seq # "+seq_nb)
                self.routing_table.seq[sender] = seq_nb
                # Parse lsp and put it in table
                # sender already in routing table and thus, already in the graph
        else:
            # Add entry to routing table
            # Parse lsp and put it in table
            #sender not in routing table and thus, not in graph
            self.routing_table.seq[sender] = seq_nb
            if sender not in self.routing_table.table:
                self.routing_table.graph.add_node(sender)

        changed = self.add_edges(tokens)
        if changed:
            self.routing_table.table = get_next_step(self.routing_table.graph, \
                                                     self.routing_table.router_name)
            self.routing_table.update()
        # Send ack to sender
        self.buffer.add_send([Type.LSACK, sender, seq_nb])
        # Forward to neighboors (LSP Packet)
        self.buffer.add_send(tokens)


    def add_edges(self, tokens):
        sender = tokens[1]
        changed = False
        i = 3
        while i < (len(tokens) - 1):
            #The edge is already in the graph
            if self.routing_table.graph.has_edge((sender, tokens[i])):
                #The edge weight isn't the same as known in the graph
                if not int(self.routing_table.graph.edge_weight((sender, tokens[i]))) == int(tokens[i+1]):
                    self.routing_table.graph.set_edge_weight((sender, tokens[i]), int(tokens[i+1]))
                    changed = True
            else:
                if not self.routing_table.graph.has_node(tokens[i]):
                    self.routing_table.graph.add_node(tokens[i])
                self.routing_table.graph.add_edge((sender, tokens[i]), int(tokens[i+1]))
                changed = True
            i += 2
            
        return changed


    def handle_ack(self, tokens, addr):
        """ Handle received lsack"""
        if len(tokens) < 3:
            logging.error("LSACK packet error")
            return
        receiver = tokens[1]
        # Find associated HOST with IP
        sender = None
        for key, value in self.routing_table.neighbours.items():
            if value[Field.HOST] == addr[0] and value[Field.PORT] == str(addr[1]):
                sender = key
        if sender is None:
            logging.error("LSACK Sender not found "+addr[0]+":"+str(addr[1]))
            return

        # Check if ACK nb is valid
        if int(tokens[2]) != int(self.routing_table.neighbours[sender][7]):
            # LSP Already aknowledged
            logging.debug("LSACK already acknowledged seq# "+tokens[2])
            return
        elif sender in self.routing_table.neighbours:
            logging.debug("LSACK received from "+sender+" seq # "+tokens[2])
            self.routing_table.neighbours[sender][5] = True
        else:
            logging.error("Received unintended LSACK ")

