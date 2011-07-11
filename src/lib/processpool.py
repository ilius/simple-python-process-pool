
from pprint import pprint, pformat
from collections import deque
from threading import RLock, Timer
from multiprocessing import Process

class ProcessPool(object):
    
    def __init__(self, max_running_procs=1, check_interval=3):
        self.__max_running_procs = max_running_procs
        self.__check_interval = check_interval
        self.__closed = False
        self.__pending = deque()
        self.__running = []
        self.__pending_lock = RLock()
        self.__running_lock = RLock()
        self.__manager_timer = Timer(self.__check_interval, self.__manage)
        self.__manager_timer.start()
    
    def __manage(self):
        print('  Inside ProcessPool.__manage')
        with self.__running_lock:
            [self.__running.remove(i) for i in self.__running if not i.is_alive()]
            self.__try_start()
            
        if not self.__closed:
            # Restart timer
            self.__manager_timer = Timer(self.__check_interval, self.__manage)
            self.__manager_timer.start()
    
    def apply_async(self, func, args=tuple(), kwargs={}):
        with self.__pending_lock:
            self.__pending.append({ 'target': func, 'args': args, 'kwargs': kwargs })
            
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
    def is_full(self):
        with self.__pending_lock:
            return self.count_running >= self.__max_running_procs
    
    @property
    def has_pending_processes(self):
        with self.__pending_lock:
            return 0 < self.count_pending
    
    @property
    def count_pending(self):
        with self.__pending_lock:
            return len(self.__pending)
    
    @property
    def count_running(self):
        with self.__running_lock:
            return len(self.__running)
    
    def __try_start(self):
        if self.__closed:
            return
        
        with self.__pending_lock:
            with self.__running_lock:
                while self.has_pending_processes and not self.is_full:
                    # Create a new Process
                    next = self.__pending.pop()
                    print('Creating next process: {0}'.format(pformat(next)))
                    p = Process(target=next['target'], args=next['args'], kwargs=next['kwargs'])
                    self.__running.append(p)
                    p.start()
                    