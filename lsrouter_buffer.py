import threading





class LsRouterBuffer:
    
    send_queue = []
    ack_queue = []

    def __init__(self):
        self.send_sem = threading.Semaphore(0)
        self.ack_sem = threading.Semaphore(0)
    
    def add_send(self, array):
        self.send_queue.append(array)
        self.send_sem.release()

    def try_pop_send(self):
        if self.send_sem.acquire(False):
            return self.send_queue.pop()
        else:
            return False

    def pop_send(self):
        self.send_sem.acquire()
        return self.send_queue.pop()
    
