#!/usr/bin/env python

import time
from pprint import pprint
import random

from lib.processpool import ProcessPool

def main():
    
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

if __name__ == '__main__':
    main()
    