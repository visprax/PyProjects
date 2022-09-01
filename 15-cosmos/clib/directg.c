#include <stdlib.h>
#include <stdio.h>
#include <math.h>

#include "directg.h"

/*
 * Initialize particles, set position in each direction in Cartesian 
 * coordinate to a random value less than 1, and set velocity of each
 * particle to zero in all directions.
 */
Particle* init_particles(size_t num_particles)
{
    Particle* particles = malloc(num_particles * sizeof(Particle));
    if (particles == NULL)
    {
        fprintf(stderr, "Error during allocating memory storage for particles.");
        exit(EXIT_FAILURE);
    }

    for (int i = 0; i < num_particles; i++)
    {
        particles[i].position[0] = (double) rand() / RAND_MAX  - 0.5;
        particles[i].position[1] = (double) rand() / RAND_MAX  - 0.5;
        particles[i].position[2] = (double) rand() / RAND_MAX  - 0.5;

        particles[i].velocity[0] = (double) rand() / RAND_MAX  - 0.5;
        particles[i].velocity[1] = (double) rand() / RAND_MAX  - 0.5;
        particles[i].velocity[2] = (double) rand() / RAND_MAX  - 0.5;

        particles[i].mass = 1.0;
    }

    return particles;
}


// Initialize forces for all particles in each directions to zero.
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

double kinetic_energy(Particle* particles, size_t num_particles)
{
    double KE = 0.0;

    for (int i = 0; i < num_particles; i++)
    {
        double Vx = particles[i].velocity[0];
        double Vy = particles[i].velocity[1];
        double Vz = particles[i].velocity[2];
        double V2 = Vx*Vx + Vy*Vy + Vz*Vz;

        KE += 0.5 * particles[i].mass * V2;
    }

    return KE;
}

double potential_energy(Particle* particles, size_t num_particles)
{
    double G  = GRAVITATIONAL_CONSTANT;
    double Rs = SOFTENING_LENGTH;
    double PE = 0.0;

    for (int i = 0; i < num_particles - 1; i++)
        for (int j = i + 1; j < num_particles; j++)
        {
            double dx = particles[j].position[0] - particles[i].position[0];
            double dy = particles[j].position[1] - particles[i].position[1];
            double dz = particles[j].position[2] - particles[i].position[2];

            double R2 = dx*dx + dy*dy + dz*dz;
            // 1 / R
            double Ri = pow(R2 + Rs*Rs, -0.5);
            
            PE += -G * particles[i].mass * particles[j].mass * Ri;
        }

    return PE;
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
    double Rs = SOFTENING_LENGTH;

    for (int i = 0; i < num_particles; i++)
    {
        forces[3 * i + 0] = 0.0;
        forces[3 * i + 1] = 0.0;
        forces[3 * i + 2] = 0.0;

        for (int j = 0; j < num_particles; j++)
            if ( j != i )
            {
                double dx = particles[j].position[0] - particles[i].position[0];
                double dy = particles[j].position[1] - particles[i].position[1];
                double dz = particles[j].position[2] - particles[i].position[2];

                double R2 = dx*dx + dy*dy + dz*dz;
                // 1 / (R2 + Rs)^(3/2)
                double Ri = pow(R2 + Rs*Rs, -1.5);

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

void directg()
{
    size_t num_particles = NUM_PARTICLES;

    double t  = 0.0;
    double dt = TIME_STEP;
    int iter = 0;

    Particle* particles = init_particles(num_particles);
    double* forces = init_forces(num_particles);

    if (COM_COORDS)
    {
        double tot_mass = 0.0;
        for (int i = 0; i < num_particles; i++)
        {
            tot_mass += particles[i].mass;
        }
        double mean_mass = tot_mass / num_particles;

        for (int i = 0; i < num_particles; i++)
        {
            double MVx = 0.0;
            double MVy = 0.0;
            double MVz = 0.0;
            for(int j = 0; j < num_particles; j++)
            {
                MVx += particles[j].mass * particles[j].velocity[0];
                MVy += particles[j].mass * particles[j].velocity[1];
                MVz += particles[j].mass * particles[j].velocity[2];
            }
            double mean_MVx = MVx / num_particles;
            double mean_MVy = MVy / num_particles;
            double mean_MVz = MVz / num_particles;
            
            particles[i].velocity[0] -= mean_MVx / mean_mass;
            particles[i].velocity[1] -= mean_MVy / mean_mass;
            particles[i].velocity[2] -= mean_MVz / mean_mass;
        }
    }

    while (t < 1.0)
    {
        compute_forces(particles, forces, num_particles);

        double KE = kinetic_energy(particles, num_particles);
        double PE = potential_energy(particles, num_particles);
        fprintf(stdout, "\nKinetic Energy: %f", KE);
        fprintf(stdout, "\nPotential Energy: %f", PE);
        fprintf(stdout, "\nTotal Energy: %f", KE+PE);

        for (int i = 0; i < num_particles; i++)
        {
            Particle* particle = &particles[i];
            double* force = &forces[3 * i];

            // Half kick
            particle->velocity[0] += 0.5 * (force[0] / particle->mass) * dt;
            particle->velocity[1] += 0.5 * (force[1] / particle->mass) * dt;
            particle->velocity[2] += 0.5 * (force[2] / particle->mass) * dt;
            
            // Drif
            particle->position[0] += particle->velocity[0] * dt;
            particle->position[1] += particle->velocity[1] * dt;
            particle->position[2] += particle->velocity[2] * dt;

            compute_forces(particles, forces, num_particles);

            particle->velocity[0] += 0.5 * (force[0] / particle->mass) * dt;
            particle->velocity[1] += 0.5 * (force[1] / particle->mass) * dt;
            particle->velocity[2] += 0.5 * (force[2] / particle->mass) * dt;
        }

        t += dt;
        iter += 1;

        if (iter % 10 == 0)
        {
            double KE = kinetic_energy(particles, num_particles);
            double PE = potential_energy(particles, num_particles);
            fprintf(stdout, "\nKinetic Energy: %f", KE);
            fprintf(stdout, "\nPotential Energy: %f", PE);
            fprintf(stdout, "\nTotal Energy: %f", KE+PE);
        }
    }

}

int main()
{
    directg();
}
