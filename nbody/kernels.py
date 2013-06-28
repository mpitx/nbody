#!/usr/bin/env python

import os
import sys
import math
import numpy as np
import pycuda.driver as cuda
import pycuda.autoinit
from pycuda.compiler import SourceModule
import jinja2
import time

MAX_THREADS = pycuda.tools.DeviceData().max_threads
BLOCK_SIZE = int(math.sqrt(MAX_THREADS))
DEV_MEM = cuda.Device(0).total_memory()

reset_template = jinja2.Template('''
    __global__ void reset_force(float *fx, float *fy)
    {
        int idx = threadIdx.x + blockIdx.x * blockDim.x;
        fx[idx] = 0.0f;
        fy[idx] = 0.0f;
    }''')
add_template = jinja2.Template('''
    __global__ void add_force(float *rx, float *vx,
                              float *fx, float *mass)
    {
        int idx = threadIdx.x + blockIdx.x * blockDim.x;
        float dx, F;
        int idy;
        for (idy = 0; idy < {{N}}; idy++)
        {
            if (idy == idx) continue;
            dx = rx[idx] - rx[idy];
            F = ({{G}} * mass[idx] * mass[idy])/
                (dx + {{EPS}} * {{EPS}});
            fx[idx] += F;
        }
    }''')
step_template = jinja2.Template('''
    __global__ void update(float *rx, float *ry, float *vx,
                           float *vy, float *fx, float *fy,
                           float *mass)
    {
        int idx = threadIdx.x + blockIdx.x * blockDim.x;
        vx[idx] += {{dt}} * fx[idx] / mass[idx];
        vy[idx] += {{dt}} * fy[idx] / mass[idx];
        rx[idx] += {{dt}} * vx[idx];
        ry[idx] += {{dt}} * vy[idx];
    }''')

def get_kernel_functions(**kwargs):
    reset_mod = SourceModule(reset_template.render(kwargs))
    add_mod = SourceModule(add_template.render(kwargs))
    step_mod = SourceModule(step_template.render(kwargs))
    reset_func = reset_mod.get_function('reset_force')
    add_func = add_mod.get_function('add_force')
    update_func = step_mod.get_function('update')
    return (reset_func, add_func, update_func,)
