#!/usr/bin/env python

import time
from pprint import pprint
import random

from lib.processpool import ProcessPool

def my_process_func(proc_index, name, iterations, sleep_interval):
    try:
        print('Inside my_process_func {0}'.format(proc_index))
        for i in range(iterations):
            time.sleep(sleep_interval)
            print('{0} says "Hi!"'.format(name))
        
    except KeyboardInterrupt:
        print('{0} says "I see KeyboardInterrupt!"'.format(name))
            
    print('{0} says "Good-bye"'.format(name))

def main():
    
    # Initialize pool
    pool = ProcessPool(max_running_procs=2)
    
    # Assign some work to the pool
    names = ['Bob', 'Jane', 'Jeremy', 'Nancy', 'Susan', 'Aaron', 'Toby', 'Tom']
    for i in range(10):
        pool.apply_async(
            func=my_process_func,
            kwargs={
                'proc_index': i,
                'name': random.choice(names),
                'iterations': 5,
                'sleep_interval': 2
            })
        
    try:
        while True:
            time.sleep(2)
            
            print("""\
  main looping -- {0}
    processes queued: {1}
    process running?: {2}""".format(
                time.time(),
                pool.count_pending,
                pool.count_running))
            
    except KeyboardInterrupt:
        print('\nmain caught KeyboardInterrupt')
        
    pool.close()
    pool.join()

if __name__ == '__main__':
    main()
    