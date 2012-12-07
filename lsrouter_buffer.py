import threading


class LsRouterBuffer:
    """ This class is a buffer. The contents of this buffer will be sent over the network """   
    send_queue = []

    def __init__(self):
        """ Initialize the semaphore to 0"""
        self.send_sem = threading.Semaphore(0)
    
    def add_send(self, array):
        """ Add the array to the queue and increments the semaphore"""
        self.send_queue.append(array)
        self.send_sem.release()

    def try_pop_send(self):
        """ Try to pop an elem from the queue. If the queue is empty, False is returned"""
        if self.send_sem.acquire(False):
            return self.send_queue.pop()
        else:
            return False
    
    def pop_send(self):
        """ Pop a element from the queue. If the sem <=0 the call is blocking"""
        self.send_sem.acquire()
        return self.send_queue.pop()
    
