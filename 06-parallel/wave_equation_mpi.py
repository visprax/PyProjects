#!/usr/bin/env ptyhon3

"""Solve 1 dimentional wave equation in parallel using MPI.

This program solves the 1D wave equation of the form:
    u := u(x, t),
    d^2u/dt^2 = c^2 * d^2u/dx^2 (utt = c^2 * uxx),
    c := propagation speed of wave

over the spatial interval [x1, x2] and time interval [t1, t2], 
with initial conditions:
    u(x, t1) = u_t1(x),
    du(x, t1)/dt = ut_t1(x)

and Dirichlet boundary condition:
    u(x1, t) = u_x1(t),
    u(x2, t) = u_x2(t)

This program uses Finite Difference Method, solving for all the values of u 
at the next time step using the values known at the previous two time steps.
Central Differences maybe used to approximate both time and space derivatives 
in the original differential equation. Thus assuming we have available the 
approximate values of u at the current and previous time steps, we may write 
a discritized version of the wave equation as follows:
    uxx(x, t) = d( u(x+dx, t) -2u(x, t) + u(x-dx, t) ) / dx^2,
    utt(x, t) = d( u(x, t+dt) -2u(x, t) + u(x, t-dt) ) / dt^2

by multiply the first equation by c^2 and using the wave equation, and solving 
for u(x, t+dt), we get:
    u(x, t+dt) = u(x+dx, t) * ( c^2 * dt^2/dx^2 )
               + u(x-dx, t) * ( c^2 * dt^2/dx^2 )
               + u(x,    t) * ( 1 - c^2*dt^2/dx^2  )
               - u(x, t-dt)

this is the equation to advance from time t to t+dt, except for the first step.
On the frist step, we only have the values of u for the initial time, but not for 
the previous time step. In this case we use the initial condition for the du/dt 
which can be approximated by a central difference that involves u(x, t+dt) and u(x, t-dt):
    du(x, t)/dt = ( u(x, t+dt) - u(x, t-dt) ) / ( 2*dt )

so we can estimate u(x, t-dt) as:
    u(x, t-dt) = u(x, t+dt) - 2*dt*du(x, t)/dt

if we replace this equation in the previous equation for u(x, t+dt), we get the equation 
for the first time step:
    u(x, t+dt) = 1/2 * u(x+dx, t) * ( c^2 * dt^2/dx^2 )
               + 1/2 * u(x-dx, t) * ( c^2 * dt^2/dx^2 )
               +       u(x,    t) * ( 1 - c^2*dt^2/dx^2 )
               + dt * du(x, t)/dt

this is the equation for advancing from time t to t+dt for the first time step.

We use MPI in order to accelerate the computation. We use domain decomposition, 
which assuming P MPI processes, divides the original interval into P subintervals, 
and each process does the computation on the interval associated with its subinterval.
However to compute the estimated solution, u(x, t+dt), at the next time step, we require 
information about u(x-dx, t) and u(x+dx, t). When process ID tries to make these estimates, 
it will need one value from process ID-1, and one value from process ID+1, before it can make 
all the updates. MPI will handle the communication between these processes.
To print a table of solution, we want each process to send its final result to the master process
(with ID=0), once all the data has been collected, the master process prints it.

Resources:
    - Solving Wave Equation:      https://people.math.sc.edu/Burkardt/c_src/wave_mpi/wave_mpi.html
    - Finite Difference Method:   https://pythonnumericalmethods.berkeley.edu/notebooks/chapter23.03-Finite-Difference-Method.html
    - Central Difference Formula: http://home.cc.umanitoba.ca/~farhadi/Math2120/Numerical%20Differentiation.pdf
"""
