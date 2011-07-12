#!/usr/bin/env python

import time
from pprint import pprint
import random

from lib.processpool import ProcessPool

def main():
    try:
        pool = ProcessPool()
        pool.close()
        pool.apply_async(lambda x: None)
        pool.join()
    except AssertionError:
        print('Handled expected exception in main3')

if __name__ == '__main__':
    main()
    