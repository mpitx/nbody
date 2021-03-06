#!/usr/bin/env python

import os
import sys
import math
import numpy as np
import pycuda.driver as cuda
from mpi4py import MPI
import nbody
import nbody.mesh as mesh
import nbody.kernels as kernels

G = 6.67e-11
EPS = 3E4
dt = 0.1
COMM = MPI.COMM_WORLD
RANK = COMM.Get_rank()

def compute(particles):
    N, R, rx, ry, vx, vy, fx, fy, m = nbody.open_galaxy()
    compute_grid(rx[particles],
                 ry[particles],
                 vx[particles],
                 vy[particles],
                 fx[particles],
                 fy[particles],
                  m[particles],
                  R)
def compute_grid(rx, ry, vx, vy, fx, fy, m, radius):
    '''Do one time step in simulation

    :param rx: numpy array of x positions
    :param ry: numpy array of y positions
    :param vx: numpy array of x velocities
    :param vy: numpy array of y velocities
    :param fx: numpy array of x forces
    :param fy: numpy array of y forces
    :param m:  numpy array of masses
    :param radius: Radius of space
    '''
    def create_mesh(radius, rx, ry, grid=None):
        # returns 64 grids
        mesh_64 = list(mesh.create_grids(16,
                                         radius,
                                         x_offset=grid[0] if grid else 0,
                                         y_offset=grid[1] if grid else 0))
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
    def kernel_mesh(grids, grid_spread):
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

    def compute_mesh(mesh, grid_spread):
        grids = []
        for i, grid in enumerate(grid_spread):
            if len(grid) > 200000:
                sub_mesh, sub_grid_spread = create_mesh(mesh[i][3],
                                                        rx[grid],
                                                        ry[grid],
                                                        grid=mesh[i])
                compute_mesh(sub_mesh, sub_grid_spread)
            total_mass = sum(m[grid])
            if total_mass == 0:
                continue
            kernel(cuda.InOut(rx[grid]),
                   cuda.InOut(ry[grid]),
                   cuda.InOut(vx[grid]),
                   cuda.InOut(vy[grid]),
                   cuda.InOut(fx[grid]),
                   cuda.InOut(fy[grid]),
                   cuda.In(m[grid]),
                   len(rx[grid]))
            center_x = sum(m[grid] * rx[grid]) / total_mass
            center_y = sum(m[grid] * ry[grid]) / total_mass
            grids.append((center_x, center_y, total_mass, i))
        kernel_mesh(grids, grid_spread)

    mesh_64, grid_spread = create_mesh(radius, rx, ry)
    compute_mesh(mesh_64, grid_spread)

def main(rank):
    particle_count = COMM.recv(source=0, tag=0)
    particles = np.zeros(particle_count, dtype=np.int32)
    COMM.Recv(particles, source=0, tag=rank)
    compute(particles)
    COMM.Barrier()

if __name__ == '__main__':
    pass
