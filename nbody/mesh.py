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

def create_grids(n, r, x_offset=0, y_offset=0):
    '''Create a list (generator) of grids given the count and radius


    :param n: number of grids to create divided by 4. n * 4 = grid count
    :param r: radius of the mesh
    :param x_offset: offset in X direction
    :param y_offset: offset in Y direction
    '''
    l = 4 * r / n
    x = list(x for x in range(int(n / 2)))
    y = list(y for y in range(int(n / 2)))
    for j in y:
        for i in x:
            yield ((-r + l * i) + x_offset,
                   ( r - l * j) + y_offset,
                   l,
                   l / 2)
