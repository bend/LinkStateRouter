import threading
import logging
import time
from type import Type


class LsRouterListener(threading.Thread):
    
    def __init__(self, socket, neighbours):
        threading.Thread.__init__(self)
        self.router_socket = socket
        self.neighbours = neighbours
        self.listen = True

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
            sender = tokens[1]
            receiver = tokens[2]
            if receiver == self.neighbours.router_name:
                if sender in self.neighbours.neighbours:
                    self.neighbours.neighbours[sender][3] = time.time()
                    self.neighbours.neighbours[sender][5] = True
                else:
                    logging.error("Received HELLO from unknown")
            else:
                logging.warning("Received HELLO not intended to router")
        elif tokens[0] == Type.LSP:
            
        elif tokens[0] == Type.LSACK:
            pass
        elif tokens[0] == Type.DATA:
            pass
        else:
            logging.error("Invalid packet received")




