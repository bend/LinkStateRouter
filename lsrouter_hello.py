import threading
import time
import logging
import math

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
        logging.info("Starting HELLO thread. Interval "+str(self.hello_interval))
        routing_table = self.routing_table.neighbours
        router_name = self.routing_table.router_name
        last_hello_timestamp = 0
        hello_update = False
        while(self.send):
            for key, value in routing_table.items():
                if value[4]:
                    if value[3] < time.time() - self.hello_interval*3:
                        # Link is dead
                        value[4] = False
                        logging.warning("Link "+key+" is inactive")
                        # Send LSP to neighbours because new dead link detected
                        self.send_lsp()
                    if last_hello_timestamp < time.time() - self.hello_interval:
                        # Send HELLO because timeout
                        self.send_hello(router_name, key, (value[0], int(value[1])))
                        hello_update = True
                    if not value[5] and value[6]<time.time() - 5:
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
        logging.debug("Sending HELLO to "+receiver)
        msg = 'HELLO '+sender+' '+receiver
        msg = msg.encode('UTF-8')
        self.router_socket.sendto(msg,addr)

    def send_lsp_one(self, receiver):
        """ Send LSP to only one sender"""
        sender = self.routing_table.router_name
        msg = 'LSP '+sender+' '+str(self.seq_nb)+' '
        neighbours_table = self.routing_table.neighbours
        # Build LSP Packet
        for key, value in neighbours_table.items():
            if value[4]:
                msg+=key+' '+value[2]+' '

        msg = msg.encode('UTF-8')
        
        value = neighbours_table[receiver]
        if value[4]:
            neighbours_table[receiver][5] = False # Ack not received for this lsp
            logging.debug("Re-sending LSP to "+key+" seq # "+str(self.seq_nb))
            self.router_socket.sendto(msg,(value[0], int(value[1])))
        self.routing_table.lsp_timestamp=time.time() #send time of the lsp
        value[6] = time.time()
        value[7] = self.seq_nb
        self.seq_nb= (self.seq_nb+1)%100



    def send_lsp(self):
        sender = self.routing_table.router_name
        msg = 'LSP '+sender+' '+str(self.seq_nb)+' '
        neighbours_table = self.routing_table.neighbours
        # Build LSP Packet
        for key, value in neighbours_table.items():
            if value[4]:
                msg+=key+' '+value[2]+' '

        msg = msg.encode('UTF-8')
        
        for key,value in neighbours_table.items():
            if value[4]:
                neighbours_table[key][5] = False # Ack not received for this lsp
                logging.debug("Sending LSP to "+key+" seq # "+str(self.seq_nb))
                self.router_socket.sendto(msg,(value[0], int(value[1])))
                neighbours_table[key][6] = time.time()
                neighbours_table[key][7] = self.seq_nb
        self.routing_table.lsp_timestamp=time.time() #send time of the lsp
        self.seq_nb= (self.seq_nb+1)%100

