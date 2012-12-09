import logging
import time
from type import *


class LsRouterTable:

    neighbours = {} #Neighbours
    table = {} # routing table : [Host: [via, last_lsp_seq_nb]]
    seq = {}
    graph = None
    update_timestamp = 0 # timestamp of the routing table
    lsp_timestamp = 0
    seq_nb = 0  # LSP seq number
    

    def add_entry(self, dest, via):
        self.table[dest] = [via]

    def __init__(self, file):
        """Reads and parses the config file. 
           the router name is accessible by self.router_name
           the router port is accessible by self.router_port
           the router neighbours is accessible by self.neighbours
           The composition of neighbours is a map structured in the 
           following way:
               [neighbourname1 : [0:host, 1:port, 2:cost, 3:timestamp_hello, 4:active?, 5:lsp_seq_nb:[lsp_timeout,lsp]],...
        """
        f = open(file,'r')
        i = 0
        for line in f:
            if i == 0:
                self.router_name = line.strip()
            elif i ==1:
                self.router_port = line.strip()
            else:
                split_line = line.strip().split(' ')
                if split_line[0] == '':
                    f.close()
                    return
                if len(split_line) != 4:
                    sys.stderr.write("Incorrect number of fields in line")
                    f.close()
                    return
                if split_line[0] in self.neighbours:
                    sys.stderr.write("Duplicate entries in config file")
                    f.close()
                    return
                else:
                    self.neighbours[split_line[0]] = split_line[1:]
                    self.neighbours[split_line[0]].append(time.time()) #timestamp hello
                    self.neighbours[split_line[0]].append(True) #active
                    self.neighbours[split_line[0]].append({})

                    self.add_entry(split_line[0], split_line[0])
            i+=1
        f.close()


    def remove_entry(self, dest):
        self.table.pop(dest)

    def update(self):
        #Will update the table
        #this should be called after updating the table
        self.update_timestamp = time.time()

