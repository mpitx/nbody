#!/usr/bin/env python

import os
import math
import numpy as np

def get_particles_in_grid(r, grid):
    x = np.intersect1d(np.where(grid[0] <= r[0])[0],
                       np.where(r[0] < grid[0] + grid[2])[0])
    y = np.intersect1d(np.where(grid[1] <= r[1])[0],
                       np.where(r[1] < grid[1] + grid[2])[0])
    return np.intersect1d(x, y)

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
