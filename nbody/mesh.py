#!/usr/bin/env python

import os
import math
import numpy as np

def get_particles_in_grid_np(bodies, grid):
    contains = lambda rx, ry, d: d[0] <= rx < d[0] + d[2] and \
                                 d[1] <= ry < d[1] + d[2]
    return (x for x in bodies if contains(x[0], x[1], grid))

def get_particles_in_grid(r, grid):
    contains = lambda r, d: d[0] <= r[0] < d[0] + d[2] and \
                            d[1] <= r[1] < d[1] + d[2]
    return (i for i in range(len(r[0])) if contains((r[0][i], r[1][i]), grid))

def create_grids(n, r):
    '''Create a list (generator) of grids given the count and radius


    :param n: number of grids to create
    :param r: radius of the mesh
    '''
    l = 4 * r / n
    x = list(x for x in range(int(n / 2)))
    y = list(y for y in range(int(n / 2)))
    for j in y:
        for i in x:
            yield (-r + l * i, r - l * j, l, l / 2)
