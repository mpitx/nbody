#!/usr/bin/env python

import os
import numpy as np

class Bodies(object):
    def __init__(self, N, R, rx, ry, vx, vy, fx, fy, m):
        self.N = N
        self.R = R
        self.rx = rx
        self.ry = ry
        self.vx = vx
        self.vy = vy
        self.fx = fx
        self.fy = fy
        self.m = m
    def get_objects(self):
        return (self.N,
                self.R,
                self.rx,
                self.ry,
                self.vx,
                self.vy,
                self.fx,
                self.fy,
                self.m,)
__data_dir = os.environ['HOME']
__header = os.path.join(__data_dir, 'header')
__rx_file = os.path.join(__data_dir, 'rx.npy')
__ry_file = os.path.join(__data_dir, 'ry.npy')
__vx_file = os.path.join(__data_dir, 'vx.npy')
__vy_file = os.path.join(__data_dir, 'vy.npy')
__fx_file = os.path.join(__data_dir, 'fx.npy')
__fy_file = os.path.join(__data_dir, 'fy.npy')
__masses_file = os.path.join(__data_dir, 'masses.npy')
__bodies = None

def get_galaxy():
    if __bodies == None:
        raise Exception("galaxy has not been read")
    return __bodies.get_objects()

def open_galaxy():
    '''Assumes being called by slave and reads the created objects from disk'''
    N = 0
    R = 0.0
    filename = ''
    with open(__header, 'r') as f:
        filename = f.readline()
        N = int(f.readline())
        R = float(f.readline())
    rx_mmap = np.memmap(__rx_file, dtype=np.float32, shape=(N,), mode='r+')
    ry_mmap = np.memmap(__ry_file, dtype=np.float32, shape=(N,), mode='r+')
    vx_mmap = np.memmap(__vx_file, dtype=np.float32, shape=(N,), mode='r+')
    vy_mmap = np.memmap(__vy_file, dtype=np.float32, shape=(N,), mode='r+')
    mass_mmap = np.memmap(__masses_file,
                          dtype=np.float32,
                          shape=(N,),
                          mode='r+')
    fx_mmap = np.memmap(__fx_file, dtype=np.float32, shape=(N,), mode='r+')
    fy_mmap = np.memmap(__fy_file, dtype=np.float32, shape=(N,), mode='r+')
    N = len(rx_mmap)
    __bodies = Bodies(N, R, rx_mmap, ry_mmap, vx_mmap, vy_mmap,
                      fx_mmap, fy_mmap, mass_mmap)
    return __bodies.get_objects()

def read_galaxy(filename='./galaxy3'):
    assert os.path.exists(filename)
    global __bodies
    R = 0
    N = 0
    with open(filename, 'r') as f:
        f.readline() # ignore first line
        for i, line in enumerate(f):
            pass
        N = i + 1
    rx_mmap = np.memmap(__rx_file, dtype=np.float32, shape=(N,), mode='w+')
    ry_mmap = np.memmap(__ry_file, dtype=np.float32, shape=(N,), mode='w+')
    vx_mmap = np.memmap(__vx_file, dtype=np.float32, shape=(N,), mode='w+')
    vy_mmap = np.memmap(__vy_file, dtype=np.float32, shape=(N,), mode='w+')
    fx_mmap = np.memmap(__fx_file, dtype=np.float32, shape=(N,), mode='w+')
    fy_mmap = np.memmap(__fy_file, dtype=np.float32, shape=(N,), mode='w+')
    mass_mmap = np.memmap(__masses_file,
                            dtype=np.float32,
                            shape=(N,),
                            mode='w+')
    with open(filename, 'r') as f:
        R = float(f.readline())
        for i, line in enumerate(f):
            line = line.strip()
            props = line.split(' ')
            rx_mmap[i] = float(props[0])
            ry_mmap[i] = float(props[1])
            vx_mmap[i] = float(props[2])
            vy_mmap[i] = float(props[3])
            mass_mmap[i] = float(props[4])
    # Flush MemMaps for slave nodes
    rx_mmap.flush()
    ry_mmap.flush()
    vx_mmap.flush()
    vy_mmap.flush()
    fx_mmap.flush()
    fy_mmap.flush()
    mass_mmap.flush()
    __bodies = Bodies(N, R, rx_mmap, ry_mmap, vx_mmap, vy_mmap,
                      fx_mmap, fy_mmap, mass_mmap)
    with open(__header, 'w') as f:
        f.write(filename)
        f.write('\n')
        f.write(str(N))
        f.write('\n')
        f.write(str(R))
    return __bodies.get_objects()

def cleanup():
    os.remove(__header)
    os.remove(__rx_file)
    os.remove(__ry_file)
    os.remove(__vx_file)
    os.remove(__vy_file)
    os.remove(__fx_file)
    os.remove(__fy_file)
    os.remove(__masses_file)
