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

def dynamic(comm, rank, nproc, npoints, local_npoints, nsteps, dt):
    """Advance the local solution for a given number of steps.

    Parameters:
        rank (int): The rank of the caller processor.
        nproc (int): Total number of processors.
        npoints (int): Total number of points.
        local_npoints (int): Total number of points for the caller processor.
        nsteps (int): Total number of steps.
        dt (float): Time step size.

    Returns:
        u1_local (numpy.array): Solution of the wave equation at the last time step, 
            as calculated by the caller processor.
    """
    # wave propagation speed
    c = 1.0
    dx = 1.0 / (npoints-1)
    alpha = c * dt/dx

    if np.abs(alpha) >= 1.0:
        if rank == 0:
            logging.error("alpha >= 1 (alpha = c*dt/dx)")
            logging.debug("c = {}".format(c))
            logging.debug("dt = {}".format(dt))
            logging.debug("dx = {}".format(dx))
            logging.debug("alpha = {}".format(alpha))
            logging.error("Computation will not be stable!")
        sys.exit(1)

    global_idx_start = int((rank * (npoints-1)) / nproc)
    global_idx_end = int(((rank+1) * (npoints-1)) / nproc)
    if rank > 0:
        global_idx_start -= 1

    local_idx_start = 0
    local_idx_end = global_idx_end  - global_idx_start

    u0_local = np.zeros(local_npoints)
    u1_local = np.zeros(local_npoints)
    u2_local = np.zeros(local_npoints)

    t = 0.0

    for global_idx in range(global_idx_start, global_idx_end+1):
        x = global_idx / (npoints-1)
        local_idx = global_idx - global_idx_start
        u1_local[local_idx] = exact_solution(x, t)

    for local_idx in range(local_idx_start, local_idx_end+1):
        u0_local[local_idx] = u1_local[local_idx]

    for step in range(1, nsteps+1):
        t = step * dt
        # use initial derivative information for the first step
        if step == 1:
            for local_idx in range(local_idx_start+1, local_idx_end):
                global_idx = global_idx_start + local_idx
                x = global_idx / (npoints-1)
                u2_local[local_idx] = u1_local[local_idx-1] * (0.5 * alpha**2) \
                                    + u1_local[local_idx+1] * (0.5 * alpha**2) \
                                    + u1_local[local_idx] * (1.0 - alpha**2) \
                                    + dt * dudt(x, t)
        # after first time step, use the two previous solutions
        else:
            for local_idx in range(local_idx_start+1, local_idx_end):
                u2_local[local_idx] = u1_local[local_idx-1] * (alpha**2) \
                                    + u1_local[local_idx+1] * (alpha**2) \
                                    + u1_local[local_idx] * 2.0 * (1.0 - alpha**2)

    # exchange the local boundary values with the left processor
    rtol_tag = 21
    ltor_tag = 12
    if rank > 0:
        comm.send(u2_local[local_idx_start+1], dest=rank-1, tag=rtol_tag)
        u2_local[local_idx_start] = comm.recv(source=rank-1, tag=ltor_tag)
    else:
        x = 0.0
        u2_local[local_idx_start] = exact_solution(x, t)

    # exchange the local boundary values with the right processor
    if rank < nproc-1:
        comm.send(u2_local[local_idx_end-1], dest=rank+1, tag=ltor_tag)
        u2_local[local_idx_end] = comm.recv(source=rank+1, tag=rtol_tag)
    else:
        x = 0.0
        u2_local[local_idx_end] = exact_solution(x, t)

    # replace next time step values
    for local_idx in range(local_idx_start, local_idx_end+1):
        u0_local[local_idx] = u1_local[local_idx]
        u1_local[local_idx] = u2_local[local_idx]

    return u1_local


def collect(comm, rank, nproc, npoints, local_npoints, nsteps, dt, u_local):
    """Send results from worker processes to root for printing."""
    global_idx_start = int((rank * (npoints-1)) / nproc)
    global_idx_end = int(((rank+1) * (npoints-1)) / nproc)
    if rank > 0:
        global_idx_start -= 1
    
    local_idx_start = 0
    local_idx_end = global_idx_end - global_idx_start

    buf = np.zeros(2, dtype=int)
    message1_tag = 10
    message2_tag = 20
    # root collects worker results into u_global array
    if rank == 0:
        u_global = np.zeros(npoints)
        for local_idx in range(local_idx_start, local_idx_end+1):
            global_idx = global_idx_start + local_idx - local_idx_start
            u_global[global_idx] = u_local[local_idx]
        
        for proc in range(1, nproc):
            # receive message1 (global index and number of values)
            buf = comm.recv(source=proc, tag=message1_tag)
            global_idx_start = buf[0]
            local_npoints_check = buf[1]
            
            if global_idx_start < 0:
                logging.critical("Consistency Error. Illegal global_idx_start value: {}".format(global_idx_start))
                sys.exit(1)
            elif npoints <= global_idx_start + local_npoints_check - 1:
                logging.critical("Consistency Error. Illegal global_idx_start+local_npoints_check: {}".format(global_idx_start+local_npoints_check))
                sys.exit(1)

            # receive message2 (values)
            u_global[global_idx_start:global_idx_start+local_npoints_check] = comm.recv(source=proc, tag=message2_tag)

        t = nsteps * dt
        logging.info("  index       x       f(x)        exact_solution")
        for global_idx in range(0, npoints):
            x = global_idx / (npoints-1)
            logging.info("  {:.4f}      {:.4f}      {:.4f}      {:.4f}".format(global_idx, x, u_global[global_idx], exact_solution(x, t)))
    
    # have workers send results to root
    else:
        buf[0] = global_idx_start
        buf[1] = local_npoints
        comm.send(buf, dest=0, tag=message1_tag)

        comm.send(u_local, dest=0, tag=message2_tag)


def exact_solution(x, t):
    """Evaluate the exact, theoretical solution."""
    c = 1.0
    uxt = np.sin(2.0 * np.pi * (x - c*t))
    return uxt

def dudt(x, t):
    """Evaluate the first order partial derivative of u(x, t), du(x, t)/dt"""
    c = 1.0
    dudt = -2.0 * np.pi * c * np.cos(2.0 * np.pi * (x - c*t))
    return dudt


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
    global_idx_start = int((rank * (npoints-1)) / nproc)
    global_idx_end = int(((rank+1) * (npoints-1)) / nproc)
    if rank > 0:
        global_idx_start -= 1
    local_npoints = global_idx_end - global_idx_start + 1
    
    # update local values
    u1_local = dynamic(comm, rank, nproc, npoints, local_npoints, nsteps, dt)

    # collect local values into global values
    collect(comm, rank, nproc, npoints, local_npoints, nsteps, dt, u1_local)

    end_time = MPI.Wtime()
    wall_time = end_time - start_time

    if rank == 0:
        logging.info("Elapsed wall clock time: {}s".format(wall_time))



if __name__ == "__main__":
    solve_wave_equation()

