import threading
import logging


class LsRouterListener(threading.Thread):
    
    def __init__(self, socket, config):
        threading.Thread.__init__(self)
        self.router_socket = socket
        self.config = config
        self.listen = True

    def run(self):
        logging.info("Starting listener thread")
        while self.listen:
            data,addr = self.router_socket.recvfrom(1024)
            if not data:
                logging.error("Error packet received from ", addr)
            else:
                p = parse(data)



    def parse(self, packet):
        return packet.split(' ')




