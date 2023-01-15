#!/usr/bin/env python3

import random
import logging

def solver():
    """Solve a linear set of equations of the form Ax=b."""
    
    N = 5
    for i in range(1000000):
        print(f"i: {i}", end="\r")
        A = [random.uniform(-10, 10) for _ in range(N*N)]
        b = [random.uniform(-10, 10) for _ in range(N)]


if __name__ == "__main__":
    solver()
    
