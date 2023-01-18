/*
 * Solve a system of linear equations (ax = b) using LAPACK dgesv.
 * For an explanation of the interface and the relevant parameters, see:
 * https://www.math.utah.edu/software/lapack/lapack-d/dgesv.html
 */

#include <stdio.h>
#include <stdlib.h>

extern void dgesv_( int* n, int* nrhs, double* a, int* lda, int* ipiv, double* b, int* ldb, int* info );

#define N 4
#define NRHS 1
#define LDA N
#define LDB N

int main() {
    int n = N, nrhs = NRHS, lda = LDA, ldb = LDB, info;

    int ipiv[N];

    // note that as dgesv is implemented in Fortran which is column-major,
    // we have to transpose the coefficients matrix before feeding to dgesv
    double a[LDA*N] = 
    {
        2,  3,  1,  5,
       -1,  2,  3, -2, 
        5,  2,  3, -3,
        1, -6, -1,  3
    };

    double b[LDB*NRHS] = {-3, -32, -47, 49};

    dgesv_(&n, &nrhs, a, &lda, ipiv, b, &ldb, &info);

    // after call to dgesv, 'b' is overwritten with the solution
    for(size_t i = 0; i < N; i++)
    {
        printf("b[%zu]: %f\n", i, b[i]);
    }

}
