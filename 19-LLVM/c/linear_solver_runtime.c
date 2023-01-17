/*
 * Solve a system of linear equations (ax = b) using Cramer's rule.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// the matrix of coefficients is of size NxN
#define N 4

// -1 to the power of x
int minus_one_power(int x)
{
    if((x % 2) == 0) return 1;

    return -1;
}

// 'ra' is the matrix 'a' with row 0 and column c removed
void reduced_a(double* a, double* ra, size_t n, size_t c)
{
    int idx = 0;
    for(size_t i = 1; i < n; i++)
        for(size_t j = 0; j < n; j++)
            if(j != c)
            {
                ra[idx] = a[n*i + j];
                idx += 1;
            }
}

// 'a' is of size nxn
double det(double* a, size_t n)
{
    if (n == 1) return a[0];

    double d = 0.0;
    for(size_t i = 0; i < n; i++)
    {
       double ra[(n-1) * (n-1)]; 
       reduced_a(a, ra, n, i);

       d += a[i] * minus_one_power(i) * det(ra, n-1);
    }
    
    return d;
}

int main()
{
    double a[N*N] = 
    {
        2, -1,  5,  1,
        3,  2,  2, -6,
        1,  3,  3, -1,
        5, -2, -3,  3
    };
    double b[N] = {-3, -32, -47, 49};
    double x[N];

    double d = det(a, N);
    printf("%f\n", d);

}
