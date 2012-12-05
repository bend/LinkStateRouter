import threading
import time
import logging
import math

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
            print("in loop")
            tosend = self.buffer.pop_send()
            self.send_data(tosend[1],tosend[2], tosend[3])
            

    def send_data(self, sender, receiver, msg):
        tosend = 'DATA '+sender+' '+receiver+' '+msg
        # TODO merge 2 tables ??
        if receiver in self.routing_table.table:
            # Get addr
            via = self.routing_table.table[receiver]
            if via[0] in self.routing_table.neighbours:
                neighbour = self.routing_table.neighbours[via[0]]
                addr = (neighbour[0], int(neighbour[1]))
            tosend = tosend.encode('UTF-8')
            self.router_socket.sendto(tosend, addr)
        else:
            logging.error("Unknown destination")



