#ifndef LIBG
#define LIBG

#include <stdlib.h>

typedef struct
{
    size_t num_particles;
    double gravitational_constant;
    double softening_length;
    double time_step;
    // set to 1 to use center of mass coordinate
    int com_coords;
} Params;

typedef struct
{
    double position[3];
    double velocity[3];
    double mass;
} Particle;

Particle* init_particles(Params params);
double* init_forces(Params params);
void compute_forces(Particle* particles, double* forces, Params params);
void directg();

double kinetic_energy(Particle* particles, Params params);
double potential_energy(Particle* particles, Params params);
double momentum(Particle* particles, Params params);

#endif // LIBG
