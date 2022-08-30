#include <stdlib.h>
#include <stdio.h>
#include <math.h>

#define NUM_PARTICLES 100
#define G 1
#define SOFTENING 0.05
#define RAND_POS() (double) rand() / RAND_MAX - 0.5

typedef struct 
{
    double position[3];
    double velocity[3];
    double mass;
} Particle;

Particle init()
{
    struct particle;

    particle.position[0] = RAND_POS();
    particle.position[1] = RAND_POS();
    particle.position[2] = RAND_POS();

    particle.velocity[0] = 0.0;
    particle.velocity[1] = 0.0;
    particle.velocity[2] = 0.0;

    particle.mass = 1.0;

    return particle;
}
