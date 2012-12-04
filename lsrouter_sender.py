import threading
import time
import logging
import math

class LsRouterSender(threading.Thread):

    def __init__(self, router):
        threading.Thread.__init__(self)
        self.router_socket = router.router_socket
        self.routing_table = router.routing_table
        self.send = True
        self.hello_interval = router.hello_interval
        self.lsp_interval = router.lsp_interval
        self.router = router

    def run(self):
        logging.info("Starting HELLO thread. Interval "+str(self.hello_interval))
        routing_table = self.routing_table.neighbours
        router_name = self.routing_table.router_name
        while(self.send):
            for key, value in routing_table.items():
                if value[5]:
                    if value[3] < time.time() - self.hello_interval*3:
                        #link is dead
                        value[5] = False
                        logging.warning("Link "+key+" is inactive")
                        # send lsp to neighbours
                        self.send_lsp()
                    else:
                        self.send_hello(router_name, key, (value[0], int(value[1])))
            time.sleep(math.floor(self.lsp_interval/6))
            if self.routing_table.timestamp < time.time() - self.lsp_interval:
               self.send_lsp()

    def send_hello(self, sender, receiver,addr):
        logging.debug("Sending HELLO to "+receiver)
        msg = 'HELLO '+sender+' '+receiver
        msg = msg.encode('UTF-8')
        self.router_socket.sendto(msg,addr)

    def send_lsp(self):
        pass


    def send_data(self, sender, receiver, msg):
        tosend = 'DATA '+sender+' '+receiver+' '+msg
        # TODO merge 2 tables ??
        if receiver in self.routing_table.neighbours:
            addr = (self.routing_table.neighbours[receiver][0], int(self.routing_table.neighbours[receiver][1]))
            tosend = tosend.encode('UTF-8')
            self.router_socket.sendto(tosend, addr)
        else:
            logging.error("Unknown destination")



