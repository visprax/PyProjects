#!/usr/bin/env python3

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
information about u(x-dx, t) and u(x+dx, t). When process rank tries to make these estimates, 
it will need one value from process rank-1, and one value from process rank+1, before it can make 
all the updates. MPI will handle the communication between these processes.
To print a table of solution, we want each process to send its final result to the master process
(with rank=0), once all the data has been collected, the master process prints it.

Resources:
    - Solving Wave Equation:      https://people.math.sc.edu/Burkardt/c_src/wave_mpi/wave_mpi.html
    - Finite Difference Method:   https://pythonnumericalmethods.berkeley.edu/notebooks/chapter23.03-Finite-Difference-Method.html
    - Central Difference Formula: http://home.cc.umanitoba.ca/~farhadi/Math2120/Numerical%20Differentiation.pdf
"""

import sys
import time
import logging
import argparse
import numpy as np
from mpi4py import MPI

def parse_arguments(comm):
    """Parse arguments.

    Parameters:
        comm (MPI communication object): MPI communication object, usually MPI.COMM_WORLD

    Returns:
        args (Namespace): argparse arguments namespace.
    """
    parser = argparse.ArgumentParser(description="Solve 1D Wave Equation.")
    parser.add_argument("dt", nargs='?', default=0.00125, type=float, help="time step size")
    parser.add_argument("npoints", nargs='?', default=401, type=float, help="total number of points")
    parser.add_argument("nsteps", nargs='?', default=4000, type=float, help="total number of steps")

    try:
        if comm.Get_rank() == 0:
            args = parser.parse_args()
        else:
            args = None
    except:
        args = None
        logging.critical("Error in parsing arguments.")
        sys.exit(1)
    finally:
        args = comm.bcast(args, root=0)

    return args

def update(rank, nproc, npoints, npoints_local, nsteps, dt):
    """Advance the local solution for a given number of steps.

    Parameters:
        rank (int): The rank of the caller processor.
        nproc (int): Total number of processors.
        npoints (int): Total number of points.
        npoints_local (int): Total number of points for the caller processor.
        nsteps (int): Total number of steps.
        dt (float): Time step size.

    Returns:
        solution (numpy array): Solution of the wave equation at the last time step, 
            as calculated by the caller processor.
    """
    # wave propagation speed
    c = 1.0
    dx = 1.0 / (npoints-1)
    alpha = c * dt/dx





def solve_wave_equation():
    """Solve the wave equation in parallel using MPI.

    Descritize the wave equation for u(x, t):
        d^2u/dt^2 -c^2 * d^2u/dx^2 = 0  for 0 < x < 1 and t > 0
    with boundary conditions:
        u(0, t) = u0(t) = sin(2*pi*(0 - c*t))
        u(1, t) = u1(t) = sin(2*pi*(1 - c*t))
    and initial conditions:
        u(x, 0)     = g(x, t=0) = sin(2*pi*x)
        du(x, 0)/dt = h(x, t=0) = 2*pi*c*cos(2*pi*x)
    by setting alpha = c*dt/dx, we have:
        u(x, t+dt) = 2u(x, t) - u(x, t-dt)
                   + alpha^2 * (u(x-dx, t) - 2u(x, t) + u(x+dx, t))
    """
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    nproc = comm.Get_size()

    logging.basicConfig(format='%(asctime)s  %(name)s  %(levelname)s: %(message)s', level=logging.INFO)

    args = parse_arguments(comm)
    if args == None:
        if rank == 0:
            logging.critical("Error in parsing arguments.")
            sys.exit(1)
    else:
        # time step size
        dt = args.dt
        # total number of points
        npoints = args.npoints
        # number of steps used to get solution at time t from t=0
        nsteps = args.nsteps

    if rank == 0:
        logging.info("Estimating a numerical solution of the wave equation using MPI.")
        logging.info("{} processes used.".format(nproc))
        logging.info("{} points are used.".format(npoints))
        logging.info("{} time steps of size {} used.".format(nsteps, dt))
        logging.info("solution computed at time {}".format(nsteps*dt))

    start_time = MPI.Wtime()

    # determine local points
    i_points_low = (rank * (npoints-1)) / p
    i_points_high = ((rank+1) * (npoints-1)) / p
    if rank > 0:
        i_points_low -= 1
    npoints_local = i_points_high - i_points_low + 1
    
    # update local values
    u1_local = update(rank, nproc, npoints, npoints_local, nsteps, dt)

    # collect local values into global values
    collect(rank, nproc, npoints, npoints_local, nsteps, dt, u1_local)

    end_time = MPI.Wtime()
    wall_time = end_time - start_time

    if rank == 0:
        logging.info("Elapased wall clock time: {}s".format(wall_time))



if __name__ == "__main__":
    solve_wave_equation()

