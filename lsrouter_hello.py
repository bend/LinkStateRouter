import threading
import time
import logging


class LsRouterHello(threading.Thread):

    def __init__(self, socket, neighbours, interval):
        threading.Thread.__init__(self)
        self.router_socket = socket
        self.neighbours = neighbours
        self.send = True
        self.interval = interval

    def run(self):
        logging.info("Starting hello thread. Interval "+str(self.interval))
        neighbours = self.neighbours.neighbours
        router_name = self.neighbours.router_name
        while(self.send):
            for key, value in neighbours.items():
                if value[5]:
                    if value[3] < time.time() - self.interval*3:
                        #link is dead
                        value[5] = False
                        logging.warning("Link "+key+" is inactive")
                    else:
                        self.send_hello(router_name, key, (value[0], int(value[1])))
            time.sleep(self.interval)

    def send_hello(self, sender, receiver,addr):
        logging.debug("Sending HELLO to "+receiver)
        msg = 'HELLO '+sender+' '+receiver
        msg = msg.encode('UTF-8')
        self.router_socket.sendto(msg,addr)

    def send_lsp(self, receiver):






