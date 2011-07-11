
from pprint import pprint, pformat
from collections import deque
from threading import RLock
from multiprocessing import Process

class ProcessPool(object):
    
    def __init__(self, max_running_procs=1):
        self.__max_running_procs = max_running_procs
        self.__closed = False
        self.__pending = deque()
        self.__running = []
        self.__pending_lock = RLock()
        self.__running_lock = RLock()
    
    def apply_async(self, func, args=None):
        self.__pending_lock.acquire()
        try:
            self.__pending.append({ 'target': func, 'args': args })
        finally:
            self.__pending_lock.release()
            
        self.__try_start()
    
    def close(self):
        """
        Marks the pool as closed in order to prevent further processes from
        starting.
        """
        self.__closed = True
    
    def join(self):
        """
        Join the current running process
        """
        pass
    
    @property
    def count_pending(self):
        self.__pending_lock.acquire()
        try:
            return len(self.__pending)
        finally:
            self.__pending_lock.release()
    
    @property
    def count_running(self):
        self.__running_lock.acquire()
        try:
            return len(self.__running)
        finally:
            self.__running_lock.release()
    
    def __try_start(self):
        if self.__closed:
            return
        
        self.__pending_lock.acquire()
        try:
            if 0 < len(self.__pending):
                self.__running_lock.acquire()
                try:
                    if self.__max_running_procs > self.count_running:
                        # Create a new Process
                        next = self.__pending.pop()
                        print('Creating next process: {0}'.format(pformat(next)))
                        p = Process(target=next['target'], args=next['args'])
                        self.__running.append(p)
                        p.start()
                finally:
                    self.__running_lock.release()
                
        finally:
            self.__pending_lock.release()