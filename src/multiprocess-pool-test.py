#!/usr/bin/env python

import time
from pprint import pprint
import random

from lib.processpool import ProcessPool

def my_process_func(proc_index, name, iterations, sleep_interval):
    try:
        print('Inside my_process_func {0}, name={1}, iterations={2}, sleep interval={3}'.format(proc_index, name, iterations, sleep_interval))
        for i in range(iterations):
            time.sleep(sleep_interval)
            print('{0} says "Hi!"'.format(name))
        
    except KeyboardInterrupt:
        addl_sleep = random.choice([3,6,9])
        print('{0} says "I see KeyboardInterrupt! Sleeping for {1} more seconds"'.format(name, addl_sleep))
        try:
            time.sleep(addl_sleep)
        except KeyboardInterrupt:
            # User got impatient and pressed Ctrl+C again
            pass
        
    print('{0} says "Good-bye"'.format(name))

def main(max_running_processes=3,
         initial_processes=20,
         chance_to_add=5,
         main_loop_interval=2,
         max_child_iterations=10,
         max_child_loop_interval=5):
    
    # Initialize pool
    pool = ProcessPool(max_running_procs=max_running_processes)
    
    # Assign some work to the pool
    names = ['Bob', 'Jane', 'Jeremy', 'Nancy', 'Susan', 'Aaron', 'Toby', 'Tom',
             'Calvin', 'David', 'Eric', 'Frank', 'Gary', 'Susan', 'Alice',
             'Betty', 'Helen']
    
    index = 0
    interval_range_top = max_child_loop_interval * 10 + 1
    for i in range(initial_processes):
        index = i
        name = random.choice(names)
        pool.apply_async(
            func=my_process_func,
            name='{0}-{1}'.format(name, index),
            kwargs={
                'proc_index': index,
                'name': name,
                'iterations': random.choice(range(max_child_iterations)),
                'sleep_interval': random.choice([round(x * 0.1, 1) for x in range(2, interval_range_top, 5)])
            })
        
    start_time = time.time()
    r = range(chance_to_add)
    s = range(100)
    
    try:
        while True:
            index = index + 1 if index > 0 else 0
            if random.choice(s) in r:
                print('Adding another process')
                name = random.choice(names)
                pool.apply_async(
                    func=my_process_func,
                    name='{0}-{1}'.format(name, index),
                    kwargs={
                        'proc_index': index,
                        'name': name,
                        'iterations': random.choice(range(15)),
                        'sleep_interval': random.choice([round(x * 0.1, 1) for x in range(2, 100, 2)])
                    })
            
            pending = pool.count_pending
            
            if 1 > pending:
                break
            
            print("""\
    main looping -- {0} sec
        processes queued: {1}
        processes running: {2}""".format(
                time.time() - start_time,
                pool.count_pending,
                pool.count_running))
            
            time.sleep(main_loop_interval)
            
    except KeyboardInterrupt:
        print('\nmain caught KeyboardInterrupt')
        
    pool.close()    
    pool.join()

def main2():
    
    def _return_tuple(a='abc', b='def', c='ghi'):
        return (a, b, c)
    
    def _on_proc_complete(a):
        print('_on_proc_complete got: {0}'.format(a))
    
    pool = ProcessPool()
    pool.apply_async(range, args=(0, 101, 20), callback=_on_proc_complete)
    pool.apply_async(_return_tuple, kwargs={ 'a': 123, 'b': 456, 'c': 789 }, callback=_on_proc_complete)
    pool.wait()
    
    pool.close()
    pool.join()
    
def main3():
    try:
        pool = ProcessPool()
        pool.close()
        pool.apply_async(lambda x: None)
        pool.join()
    except AssertionError:
        print('Handled expected exception in main3')

if __name__ == '__main__':
    main(initial_processes=10, max_child_iterations=5)
    main2()
    main3()
    