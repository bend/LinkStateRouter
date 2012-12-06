import threading
import logging
import time
from graph import graph
from dijkstra import *
from type import Type


class LsRouterListener(threading.Thread):
    
    def __init__(self, router_socket, routing_table, buffer):
        threading.Thread.__init__(self)
        self.router_socket = router_socket
        self.routing_table = routing_table
        self.buffer = buffer
        self.listen = True
        self.graph = graph()

    def run(self):
        logging.info("Starting listener thread")
        while self.listen:
            data,addr = self.router_socket.recvfrom(1024)
            if not data:
                logging.error("Error packet received from ", addr)
            else:
                self.package_handling(data, addr)

    def package_handling(self, packet, addr):
        packet = packet.decode('UTF-8')
        tokens = packet.split(' ')
        if tokens[0] == Type.HELLO:
            logging.debug("Received HELLO packet from " + tokens[1])
            if len(tokens) != 3:
                logging.error("Packet error")
            sender = tokens[1]
            receiver = tokens[2]
            if receiver == self.routing_table.router_name:
                if sender in self.routing_table.neighbours:
                    self.routing_table.neighbours[sender][3] = time.time()
                    self.routing_table.neighbours[sender][4] = True
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
                logging.error("Packet error")
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
        sender = tokens[1]
        seq_nb = tokens[2]
        # Keep track of seq to avoid multiple receive and send of lsack
        if sender == self.routing_table.router_name:
            # Skip forwarded packet that was initited by this router
            return
        if sender in self.routing_table.table:
            if self.routing_table.table[sender][1] == seq_nb:
                # LSP already received, skip it
                return
            else:
                # LSP not received already, update seq num
                self.routing_table.table[sender][1] = seq_nb
                # Parse lsp and put it in table
                # sender already in routing table and thus, already in the graph
                
        else:
            # Add entry to routing table
            #TODO What to do here ??
            # Parse lsp and put it in table
            #sender not in routing table and thus, not in graph
            self.graph.add_node(sender)

        
        changed = self.add_edges(token)
        if changed:
            self.routing_table.table = get_next_step(graph, self.self.routing_table.router_name)
        
        # Send ack to sender
        self.buffer.add_send([Type.LSACK, sender, seq_nb])
        # Forward to neighboors
        self.buffer.add_send(tokens)


    def add_edges(self, tokens):
        sender = tokens[1]
        changed = False
        i = 3
        while i < len(tokens):
            #The edge is already in the graph
            if self.graph.has_edge((sender, tokens[i])):
                #The edge weight is the same as known in the graph
                if self.graph.edge_weight((sender, tokens[i])) != token[i+1]:
                    self.graph.set_edge_weight(self, (sender, tokens[i]), token[i+1])
                    changed = True
            else:
                self.graph.add_edge((sender, tokens[i]),token[i+1])
                changed = True
            i += 2
        return changed


    def handle_ack(self, tokens, addr):
        if len(tokens) < 3:
            logging.error("LSACK packet error")
            return
        receiver = tokens[1]
        # Find associated HOST with IP
        sender = None
        for key, value in self.routing_table.neighbours.items():
            if value[0] == addr[0] and value[1] == str(addr[1]):
                sender = key
        if sender is None:
            logging.error("Sender not found "+addr[0]+":"+str(addr[1]))
            return

        logging.debug("LSACK received from "+sender+" seq # "+tokens[2])

        # Check if ACK nb is valid
        if tokens[2] != self.routing_table.neighbours[sender][7]:
            # LSP Already aknowledged
            return
        elif sender in self.routing_table.neighbours:
            self.routing_table.neighbours[sender][5] = True
        else:
            logging.error("Received unintended LSACK ")

