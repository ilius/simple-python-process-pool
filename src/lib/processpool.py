
from collections import deque
from threading import RLock, Timer
from multiprocessing import Process, Queue
import time

class ProcessPool(object):
    
    def __init__(self, max_running_procs=1, check_interval=1, always_finish=False):
        self.__max_running_procs = max_running_procs
        self.__check_interval = check_interval
        self.__always_finish = always_finish
        self.__closed = False
        self.__pending = deque()
        self.__running = {}
        self.__pending_lock = RLock()
        self.__running_lock = RLock()
        Timer(self.__check_interval, self.__manage).start()
    
    def is_running(self, name):
        try:
            procInfo = self.__running[name]
        except KeyError:
            return False
        else:
            return procInfo['process'].is_alive()
    
    @property
    def is_closed(self):
        return self.__closed
    
    @property
    def always_finish(self):
        return self.__always_finish
    
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
            
    def __manage(self):
        with self.__running_lock:
            for name, info in self.__running.items():
                if info['process'].is_alive():
                    continue
                if info['callback']:
                    info['callback'](info['queue'].get())
                del self.__running[name]
            
            self.__try_start()
        
        if not self.is_closed:
            # Restart timer
            Timer(self.__check_interval, self.__manage).start()
    
    def apply_async(self, func, name, args=tuple(), kwargs={}, callback=None):
        assert not self.is_closed
            
        with self.__pending_lock:
            self.__pending.append({
                'target': func,
                'name': name,
                'args': args,
                'kwargs': kwargs,
                'callback': callback
            })
            
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
        try:
            with self.__running_lock:
                for i in self.__running.values(): i['process'].join()
        except KeyboardInterrupt:
            # User probably got impatient and pressed Ctrl+C again
            pass
        
    def wait(self):
        while self.has_pending_processes:
            time.sleep(1)
    
    def __try_start(self):
        
        def _wrapper(func, queue):
            def _inner(*args, **kwargs):
                try:
                    result = func(*args, **kwargs)
                    queue.put(result)
                finally:
                    queue.close()

            return _inner
        
        if self.is_closed and not self.always_finish:
            return
        
        with self.__pending_lock:
            with self.__running_lock:
                while self.has_pending_processes and not self.is_full:
                    # Create a new Process
                    next = self.__pending.pop()
                    q = Queue()
                    p = Process(
                        target=_wrapper(func=next['target'], queue=q),
                        args=next['args'],
                        kwargs=next['kwargs'])
                    
                    p.name = next['name']
                    
                    self.__running[next['name']] = {
                        'name': next['name'],
                        'process': p,
                        'queue': q,
                        'callback': next['callback'],
                    }
                    p.start()
                    
