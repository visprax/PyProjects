"""Decorator to print usage and performance statistics."""

import os
import logging
import tracemalloc
from functools import wraps
from time import perf_counter

logger = logging.getLogger("usage")

def usagestat(func):
    """Spit out usage statistics of a decorated context."""
    # makes wrapping func 'systematic', func.__name__ 
    # and func.__doc__ won't be gorged by decorator.
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        tracemalloc.start()
        tstart = perf_counter()
        func(*args, **kwargs)
        current_mem, peak_mem = tracemalloc.get_traced_memory()
        tend = perf_counter()
        logger.debug(f"function: {func.__name__} - execution time:    {tend - tstart:.4f} s")
        logger.debug(f"function: {func.__name__} - memory usage:      {current_mem / (1024 * 1024):.4f} MiB")
        logger.debug(f"function: {func.__name__} - memory peak usage: {peak_mem / (1024 * 1024):.4f} MiB")
        tracemalloc.stop()
    return func_wrapper




# TODO: make the part where performance is measured a  contextlib
# @usagestat
with os.scandir('.') as entries:
    for entry in entries:
        print(f"{entry.name}: {entry.stat().st_size} B")
