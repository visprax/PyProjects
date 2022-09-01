#ifndef DIRECTG
#define DIRECTG

#include <stdlib.h>

#define NUM_PARTICLES 100
#define GRAVITATIONAL_CONSTANT 1.0
#define SOFTENING_LENGTH 0.05
#define TIME_STEP 1e-4
// set to 1 to use center of mass coordinates
#define COM_COORDS 0

typedef struct
{
    double position[3];
    double velocity[3];
    double mass;
} Particle;

Particle* init_particles(size_t num_particles);
double* init_forces(size_t num_particles);
double kinetic_energy(Particle* particles, size_t num_particles);
double potential_energy(Particle* particles, size_t num_particles);
void compute_forces(Particle* particles, double* forces, size_t num_particles);
void directg();

#endif // DIRECTG
