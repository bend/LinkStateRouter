class Type:
    ''' 
    Enumeration of the different types of message
    '''
    HELLO = "HELLO"
    LSP   = "LSP"
    LSP_ONE   = "LSP_ONE"
    LSACK = "LSACK"
    DATA  = "DATA"

class Field:
    HOST = 0        # Host
    PORT = 1        # Port
    COST = 2        # Cost
    TSH = 3         # Timestamp Hello
    ACTIVE = 4      # Active ?
    ACKR = 5        # Ack received ?
    TLSP = 6        # Timestamp LSP
    LSPNB = 7       # LSP number
