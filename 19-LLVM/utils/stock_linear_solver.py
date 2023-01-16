#!/usr/bin/env python3

import random
import logging

def det(a, n):
    """Recursive calculation of an nxn square matrix determinant,
    using Laplace's expansion formula.
    """
    if n == 1:
        return a[0][0]
    d = 0
    for i in range(n):
        c = a[:]
        del c[i]
        d += a[i][0] * (-1)**i * det([r[1:] for r in c], n-1)
    return d

def cramer_solve(a, b):
    """Solve a system of linear equation of the form Ax=b using cramer's rule."""
    n = len(b)
    d = det(a, n)
    if d == 0:
        x = []
    else:
        x = [det([p[0:i]+[q]+p[i+1:] for p,q in zip(a, b)], n) / d for i in range(n)]
    return x

if __name__ == "__main__":
    a = [[ 2, -1,  5,  1],
         [ 3,  2,  2, -6],
         [ 1,  3,  3, -1],
         [ 5, -2, -3,  3]]
    b = [-3, -32, -47, 49]

    x = cramer_solve(a, b)
    print(x)
