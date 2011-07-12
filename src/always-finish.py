#!/usr/bin/env python

import time
from pprint import pprint
import random

from lib.processpool import ProcessPool

def main():
    def _sleep(index):
        print('{0} sleeping'.format(index))
        time.sleep(2)
        
    pool = ProcessPool(max_running_procs=2, always_finish=True)
    for i in range(10):
        pool.apply_async(func=_sleep, args=(i,))

    pool.close()
    pool.join()

if __name__ == '__main__':
    main()
    