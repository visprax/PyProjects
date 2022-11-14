"""Decorator to print usage and performance statistics."""

import os
from functools import wraps
from time import perf_counter

def usagestat(func):
    # makes wrapping func 'systematic', func.__name__ 
    # and func.__doc__ won't be gorged by decorator.
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        print("test")
        func(*args, **kwargs)
    return func_wrapper




with os.scandir('.') as entries:
    for entry in entries:
        print(f"{entry.name}: {entry.stat().st_size} B")
