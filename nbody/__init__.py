#!/usr/bin/env python

import os
import numpy as np

def read_galaxy_np(filename='./galaxy3'):
    assert os.path.exists(filename)
    bodies = []
    N = 0
    R = 0
    with open(filename, 'r') as f:
        R = float(f.readline())
        lines = f.readlines()
        N = len(lines)
        for line in lines:
            line = line.strip()
            props = line.split(' ')
            #( 0,  1,  2,  3,  4,  5, 6)
            #(rx, ry, vx, vy, fx, fy, m)
            bodies.append((float(props[0]), float(props[1]),
                           float(props[2]), float(props[3]),
                           0, 0, float(props[4])))
    bodies = np.array(bodies, dtype=np.float32)
    return (N, R, bodies)

def read_galaxy(filename='./galaxy3'):
    assert os.path.exists(filename)
    R = 0
    rx = []
    ry = []
    vx = []
    vy = []
    fx = []
    fy = []
    masses = []
    colors = []
    N = 0
    with open(filename, 'r') as f:
        R = float(f.readline())
        lines = f.readlines()
        N = len(lines)
        for line in lines:
            line = line.strip()
            props = line.split(' ')
            rx.append(float(props[0]))
            ry.append(float(props[1]))
            vx.append(float(props[2]))
            vy.append(float(props[3]))
            masses.append(float(props[4]))
            colors.append((int(props[5]),
                          int(props[6]),
                          int(props[7])))
    return (N,
            R,
            np.array(rx),
            np.array(ry),
            np.array(vx),
            np.array(vy),
            np.zeros(len(rx)),
            np.zeros(len(rx)),
            np.array(masses),
            np.array(colors),)
