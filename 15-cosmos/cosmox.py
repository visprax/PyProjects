#!/usr/bin/env python3

import ctypes

clib = ctypes.CDLL("clib/arrays.so")

print(clib.square(10));
