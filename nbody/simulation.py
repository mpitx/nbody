#!/usr/bin/env python

import os
import sys
import math
import numpy as np
import nbody
import nbody.mesh as mesh

G = 6.67e-11
EPS = 3E4
dt = 0.1

def add_force(rx, ry, fx, fy, m):
    dx = rx[1] - rx[0]
    dy = ry[0] - ry[0]
    dist = math.sqrt(dx ** 2 + dy ** 2)
    F = (G * m[0] * m[0]) / (dist ** 2 + EPS ** 2)
    return (fx + dx / dist, fy + dy / dist)

def simulation(rx, ry, vx, vy, fx, fy, m, radius, steps=1):
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
        simulation_step(rx, ry, vx, vy, fx, fy, m, radius)

def simulation_step(rx, ry, vx, vy, fx, fy, m, radius):
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
    def __add_force(i, j):
        fx[i], fy[i] = add_force((rx[i], rx[j]),
                                 (ry[i], ry[j]),
                                 fx[i], fy[i],
                                 (m[i], m[j]))
    def grid_direct(rx, ry, vx, vy, fx, fy, m):
        fx = np.zeros(len(rx))
        fy = np.zeros(len(rx))
        for i in range(len(rx)):
            for j in range(len(rx)):
                if i != j:
                    __add_force(i, j)
        vx = vx + dt * fx / m
        vy = vy + dt * fy / m
        rx = rx + dt * vx
        ry = ry + dt * vy
    mesh_64 = mesh.create_grids(16, radius) # returns 64 grids
    grid_spread = list(list(x) for x in
                       (mesh.get_particles_in_grid((rx, ry), y)
                       for y in mesh_64))
    grids = []
    for grid in grid_spread:
        grid_direct(rx[grid],
                    ry[grid],
                    vx[grid],
                    vy[grid],
                    fx[grid],
                    fy[grid],
                    m[grid])
    for i, grid in enumerate(grid_spread):
        total_mass = sum(m[grid])
        if total_mass == 0:
            continue
        center_x = sum(m[grid] * rx[grid]) / total_mass
        center_y = sum(m[grid] * ry[grid]) / total_mass
        grids.append((center_x, center_y, total_mass, i))

    for a in grids:
        grid = grid_spread[a[3]]
        a_fx = 0
        a_fy = 0
        for b in grids:
            if a != b:
                a_fx, a_fy = add_force((a[0], b[0]),
                                       (a[1], b[1]),
                                       a_fx, a_fy,
                                       (a[2], b[2]))
        vx[grid] = vx[grid] + dt * a_fx / m[grid]
        vy[grid] = vy[grid] + dt * a_fx / m[grid]
        rx[grid] = rx[grid] + dt * vx[grid]
        ry[grid] = ry[grid] + dt * vy[grid]

def main(args):
    assert len(args) >= 1
    N, R, rx, ry, vx, vy, fx, fy, m, c = nbody.read_galaxy(filename=args[0])
    simulation(rx, ry, vx, vy, fx, fy, m, R)

if __name__ == '__main__':
    main(sys.argv[1:])
