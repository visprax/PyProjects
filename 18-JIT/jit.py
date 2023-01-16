#!/usr/bin/env python3

import sys
import ctypes
import logging

# TODO: page-aligned memory?

print(f"detected platform: {sys.platform}")

if sys.platform.startswith("darwin"):
    libc = ctypes.cdll.LoadLibrary("libc.dylib")
    # TODO: comments on each macro
    _SC_PAGESIZE = 29
    MAP_ANONYMOUS = 0x1000
    MAP_PRIVATE = 0x0002
    PROT_EXEC = 0x04
    PROT_NONE = 0x00
    PROT_READ = 0x01
    PROT_WRITE = 0x02
    MAP_FAILED = -1
elif sys.platform.startswith("linux"):
    libc = ctypes.cdll.LoadLibrary("libc.so.6")
    _SC_PAGESIZE = 30
    MAP_ANONYMOUS = 0x20
    MAP_PRIVATE = 0x0002
    PROT_EXEC = 0x04
    PROT_NONE = 0x00
    PROT_READ = 0x01
    PROT_WRITE = 0x02
    MAP_FAILED = -1
    print(f"libc loaded: {libc}")
else:
    raise RuntimeError(f"Unsupported platform: {platform}")
