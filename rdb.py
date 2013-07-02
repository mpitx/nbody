#!/usr/bin/env python

import sys
import nbody
import nbody.master as master
import nbody.slave as slave
from mpi4py import MPI

COMM = MPI.COMM_WORLD
SIZE = COMM.Get_size()
RANK = COMM.Get_rank()

if __name__ == '__main__':
    if RANK == 0:
        import pdb
        pdb.set_trace()
        master.main(sys.argv[1:], SIZE - 1) # SIZE - master
    else:
        slave.main(RANK)
