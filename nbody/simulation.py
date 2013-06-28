#!/usr/bin/env python

import os
import sys
import math
import numpy as np
import nbody

G = 6.67e-11
EPS = 3E4
dt = 0.1

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
    def add_force(i, j):
        dx = rx[j] - rx[i]
        dy = ry[j] - ry[i]
        dist = math.sqrt(dx ** 2 + dy ** 2)
        F = (G * m[i] * m[j]) / (dist ** 2 + EPS ** 2)
        fx[i] = fx[i] + dx / dist
        fy[i] = fy[i] + dy / dist

    fx = np.zeros(len(rx))
    fy = np.zeros(len(rx))
    for i in range(len(rx)):
        for j in range(len(rx)):
            if i != j:
                add_force(i, j)
    vx = vx + dt * fx / m
    vy = vy + dt * fy / m
    rx = rx + dt * vx
    ry = ry + dt * vy

def main(args):
    assert len(args) >= 1
    N, R, rx, ry, vx, vy, fx, fy, m, c = nbody.read_galaxy(filename=args[0])
    simulation(rx, ry, vx, vy, fx, fy, m, R)

if __name__ == '__main__':
    main(sys.argv[1:])
