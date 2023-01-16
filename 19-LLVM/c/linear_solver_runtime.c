/*
 * Solve a system of linear equations using Cramer's rule.
 */

#include <stdio.h>

#define N 5

double det(double *a, int n)
{
    if (n == 1) return a[0];

    double d = 0.0;
    for(int i = 0; i < n; i++)
    {

    }
    
    return d;
}

int main()
{
    double a[N*N] = {
        2, -1,  5,  1,
        3,  2,  2, -6,
        1,  3,  3, -1,
        5, -2, -3,  3
    };
    double b[N] = {-3, -32, -47, 49};
    double x[N];
}
