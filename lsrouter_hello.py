import threading
import time
import logging


class LsRouterHello(threading.Thread):

    def __init__(self, socket, config, interval):
        threading.Thread.__init__(self)
        self.router_socket = socket
        self.config = config
        self.send = True
        self.interval = interval

    def run(self):
        logging.info("Starting hello thread. Interval "+str(self.interval))
        neighbours = self.config.neighbours
        router_name = self.config.router_name
        while(self.send):
            for key, value in neighbours.items():
                self.send_hello(router_name, key, (value[0], int(value[1])))
            time.sleep(self.interval)

    def send_hello(self, sender, receiver,addr):
        logging.debug("Sending HELLO to "+receiver)
        msg = 'HELLO '+sender+' '+receiver
        self.router_socket.sendto(bytes(msg, 'UTF-8'),addr)





