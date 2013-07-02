#!/usr/bin/env python

import os
import sys
import math
import numpy as np
import pycuda.driver as cuda
from mpi4py import MPI
import nbody
import nbody.slave as slave
import nbody.mesh as mesh
import nbody.kernels as kernels

G = 6.67e-11
EPS = 3E4
dt = 0.1
COMM = MPI.COMM_WORLD

def simulation(rx, ry, vx, vy, fx, fy, m, radius, size, steps=1):
    '''Do one time step in simulation

    All arrays _must_ be of the same size

    :param rx: numpy array of x positions
    :param ry: numpy array of y positions
    :param vx: numpy array of x velocities
    :param vy: numpy array of y velocities
    :param fx: numpy array of x forces
    :param fy: numpy array of y forces
    :param m:  numpy array of masses
    :param radius: radius of space
    :param steps: Number of time steps simulation should complete
    '''
    assert len(rx) == len(ry) \
        == len(vx) == len(vy) \
        == len(fx) == len(fy) \
        == len(m)
    for i in range(steps):
        simulation_step(rx, ry, vx, vy, fx, fy, m, radius, size)

def simulation_step(rx, ry, vx, vy, fx, fy, m, radius, size):
    def create_mesh(radius, rx, ry):
        mesh_64 = mesh.create_grids(16, radius) # returns 64 grids
        grid_spread = list(list(x) for x in
                            (mesh.get_particles_in_grid((rx, ry), y)
                            for y in mesh_64))
        return (mesh_64, grid_spread,)
    block = (16, 16, 1)
    def kernel(rx, ry, vx, vy, fx, fy, m, N):
        reset, add, step = kernels.get_kernel_functions(G=G,
                                                        dt=dt,
                                                        N=N,
                                                        EPS=EPS)
        reset(rx, ry, block=block)
        add(rx, vx, fx, m, block=block)
        add(ry, vy, fy, m, block=block)
        step(rx, ry, vx, vy, fx, fy, m, block=block)
    def kernel_mesh(grids):
        grids_rx = np.array(list(x[0] for x in grids))
        grids_ry = np.array(list(x[1] for x in grids))
        grids_vx = np.zeros_like(grids_rx)
        grids_vy = np.zeros_like(grids_rx)
        grids_fx = np.zeros_like(grids_rx)
        grids_fy = np.zeros_like(grids_ry)
        grids_m = np.array(list(x[2] for x in grids))
        N = len(grids_rx)
        add = kernels.get_kernel_functions(G=G, dt=dt, N=N, EPS=EPS)[1]
        add(cuda.InOut(grids_rx),
            cuda.InOut(grids_vx),
            cuda.InOut(grids_fx),
            cuda.In(grids_m), block=block)
        add(cuda.InOut(grids_ry),
            cuda.InOut(grids_vy),
            cuda.InOut(grids_fy),
            cuda.In(grids_m), block=block)
        for i, g in enumerate(grids):
            grid = grid_spread[g[3]]
            N = len(rx[grid])
            step = kernels.get_kernel_functions(G=G, dt=dt, N=N, EPS=EPS)[2]
            step(cuda.InOut(rx[grid]),
                 cuda.InOut(ry[grid]),
                 cuda.InOut(vx[grid]),
                 cuda.InOut(vy[grid]),
                 cuda.In(np.ones_like(rx[grid]) * grids_fx[i]),
                 cuda.In(np.ones_like(rx[grid]) * grids_fy[i]),
                 cuda.In(m[grid]), block=block)

    def compute_mesh(grid_spread):
        grids = [] # [(c_x, c_y, mass, index),...]
        for i, grid in enumerate(grid_spread):
            total_mass = sum(m[grid])
            if total_mass == 0:
                continue
            center_x = sum(m[grid] * rx[grid]) / total_mass
            center_y = sum(m[grid] * ry[grid]) / total_mass
            grids.append((center_x, center_y, total_mass, i))
        M = len(grids)
        grids_left = M
        assigned_grids = list([] for i in range(size))
        # 'round robin' assign
        while grids_left > 0:
            for i in range(size):
                assigned_grids[i].append(grid_spread[grids[M-grids_left][3]])
                grids_left = grids_left - 1
                if grids_left <= 0:
                    break
        for i, grid in enumerate(assigned_grids):
            to_rank = 1 + i
            np_grid = np.array(grid)
            COMM.send(np_grid, dest=to_rank, tag=to_rank)
        COMM.Barrier()
        kernel_mesh(grids)
    mesh_64, grid_spread = create_mesh(radius, rx, ry)
    compute_mesh(grid_spread)

def main(args, size):
    assert len(args) >= 1
    N, R, rx, ry, vx, vy, fx, fy, m = nbody.read_galaxy(filename=args[0])
    simulation(rx, ry, vx, vy, fx, fy, m, R, size)
    nbody.cleanup()

if __name__ == '__main__':
    main(sys.argv[1:], 1)
