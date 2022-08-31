#include <stdlib.h>
#include <stdio.h>
#include <math.h>

#define NUM_PARTICLES 100
#define GRAVITATIONAL_CONSTANT 1.0
#define SOFTENING_FACTOR 0.05

typedef struct 
{
    double position[3];
    double velocity[3];
    double mass;
} Particle;

/*
 * Initialize particles, set position in each direction in Cartesian 
 * coordinate to a random value less than 1, and set velocity of each
 * particle to zero in all directions.
 */
Particle* init_particles(size_t size)
{
    Particle* particles = malloc(size * sizeof(Particle));
    if (particles == NULL)
    {
        fprintf(stderr, "Error during allocating memory storage for particles.");
        exit(EXIT_FAILURE);
    }

    for (int i = 0; i < size; i++)
    {
        particles[i].position[0] = (double) rand() / RAND_MAX  - 0.5;
        particles[i].position[1] = (double) rand() / RAND_MAX  - 0.5;
        particles[i].position[2] = (double) rand() / RAND_MAX  - 0.5;

        particles[i].velocity[0] = 0.0;
        particles[i].velocity[1] = 0.0;
        particles[i].velocity[2] = 0.0;

        particles[i].mass = 1.0;
    }

    return particles;
}

/*
 * Initialize forces for all particles in each directions to zero.
 */
double* init_forces(size_t num_particles)
{
    double* forces = malloc(3 * num_particles * sizeof(double));
    if (forces == NULL)
    {
        fprintf(stderr, "Error during allocating memory storage for forces.");
        exit(EXIT_FAILURE);
    }

    for (int i = 0; i < 3 * num_particles; i++) forces[i] = 0.0;

    return forces;
}

/*
 * Calculate force on particle i due to particle j 
 * in each Cartesian coordinate axis, (x, y, z) is
 * the vector pointing from particle i to j which is
 * the direction of the gravitational force. 
 */
void compute_forces(Particle* particles, double* forces, size_t num_particles)
{
    double G  = GRAVITATIONAL_CONSTANT;
    double Rs = SOFTENING_FACTOR;

    for (int i = 0; i < num_particles; i++)
    {
        forces[3 * i + 0] = 0.0;
        forces[3 * i + 1] = 0.0;
        forces[3 * i + 2] = 0.0;

        for (int j = 0; j < num_particles; j++)
        {
            double dx = particles[j].position[0] - particles[i].position[0];
            double dy = particles[j].position[1] - particles[i].position[1];
            double dz = particles[j].position[1] - particles[i].position[2];

            double R2 = dx*dx + dy*dy + dz*dz;
            /* 1 / (R2 + Rs)^(3/2) */
            double Ri = pow(R2 + Rs, -1.5);

            double M2 = particles[j].mass * particles[i].mass;

            double Fx = G * M2 * Ri * dx;
            double Fy = G * M2 * Ri * dy;
            double Fz = G * M2 * Ri * dz;

            forces[3 * i + 0] += Fx;
            forces[3 * i + 1] += Fy;
            forces[3 * i + 2] += Fz;
        }
    }
}

void direct_nbody()
{
    size_t num_particles = NUM_PARTICLES;

    Particle* particles = init_particles(num_particles);
    double* forces = init_forces(num_particles);

    double t  = 0.0;
    double dt = 1e-4;
    int iter = 0;

    while (t < 1.0)
    {
        compute_forces(particles, num_particles);

        for (int i = 0; i < num_particles; i++)
        {
            Particle* particle = &particles[i];
            double* force = &forces[3 * i];

            particle->velocity[0] += 0.5 * (force[0] / particle->mass) * dt;
            particle->velocity[1] += 0.5 * (force[1] / particle->mass) * dt;
            particle->velocity[2] += 0.5 * (force[2] / particle->mass) * dt;

            particle->position[0] += particle->velocity[0] * dt;
            particle->position[1] += particle->velocity[1] * dt;
            particle->position[2] += particle->velocity[2] * dt;

            compute_forces(particles, num_particles);

            particle->velocity[0] += 0.5 * (force[0] / particle->mass) * dt;
            particle->velocity[1] += 0.5 * (force[1] / particle->mass) * dt;
            particle->velocity[2] += 0.5 * (force[2] / particle->mass) * dt;
        }

        t += dt;
        iter += 1;
    }
}

int main()
{

    /*
     *printf("particle 1's mass: %f\n", particles[0].mass);
     *printf("particle 2's x: %f\n", particles[1].position[0]);
     *printf("particle 3's vy: %f\n", particles[2].velocity[1]);
     *printf("particle 4's fz: %f\n", forces[3 * 3 + 2]);
     */
}
