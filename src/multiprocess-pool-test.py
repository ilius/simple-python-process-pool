#!/usr/bin/env python

import sys
import time
#import multiprocessing
from pprint import pprint

from setproctitle import setproctitle

class Pool(object):
    
    def __init__(self):
        self.__queue = None
    
    def apply_async(self, func, args):
        pprint(args)
    
    def close(self):
        pass
    
    def join(self):
        pass

def my_process_func(proc_index):
    try:
        setproctitle('mp-pool-test-{0}'.format(proc_index))
        print('Inside my_process_func ({0})'.format(proc_index))
        for i in range(10):
            time.sleep(2)
            print('my_process_func ({0}) looping'.format(proc_index))
        print('Leaving my_process_func ({1})'.format(proc_index))
        sys.stdout.flush()
    except KeyboardInterrupt:
        pass

def main():
    
    # Initialize pool
    #pool = multiprocessing.Pool(processes=1, maxtasksperchild=1)
    pool = Pool()
    
    # Assign some work to the pool
    for i in range(10):
        pool.apply_async(func=my_process_func, args=(i,))
        
    try:
        while True:
            time.sleep(2)
            #print('main looping {0}'.format(time.time()))
    except KeyboardInterrupt:
        print('\nmain caught KeyboardInterrupt')
        
    pool.close()
    pool.join()

if __name__ == '__main__':
    setproctitle('mp-pool-test')
    main()
    