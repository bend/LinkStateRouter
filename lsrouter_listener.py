import threading
import logging
import time
from type import Type


class LsRouterListener(threading.Thread):
    
    def __init__(self, router_socket, routing_table, buffer):
        threading.Thread.__init__(self)
        self.router_socket = router_socket
        self.routing_table = routing_table
        self.buffer = buffer
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
            if len(tokens) != 3:
                logging.error("Packet error")
            sender = tokens[1]
            receiver = tokens[2]
            if receiver == self.routing_table.router_name:
                if sender in self.routing_table.neighbours:
                    self.routing_table.neighbours[sender][3] = time.time()
                    self.routing_table.neighbours[sender][5] = True
                else:
                    logging.error("Received HELLO from unknown")
            else:
                logging.warning("Received HELLO not intended to router")
        elif tokens[0] == Type.LSP:
            pass           
        elif tokens[0] == Type.LSACK:
            pass
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




