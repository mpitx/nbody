#!/bin/sh

for i in $(seq 0 3)
do
    #echo "2k run ${i}"
    #/usr/bin/time mpi_run.py python2 run.py \
     #~/Data/in/nbody/galaxy3 2> ~/Data/out/2k_cudampi_p3m_${i}
    echo "20k run ${i}"
    /usr/bin/time mpi_run.py python2 run.py \
     ~/Data/in/nbody/galaxy20k 2> ~/Data/out/20k_cudampi_p3m_${i}
    echo "200k run ${i}"
    /usr/bin/time mpi_run.py python2 run.py \
     ~/Data/in/nbody/galaxy200k 2> ~/Data/out/200k_cudampi_p3m_${i}
    echo "2m run ${i}"
    /usr/bin/time mpi_run.py python2 run.py \
     ~/Data/in/nbody/galaxy2m 2> ~/Data/out/2m_cudampi_p3m_${i}
    echo "20m run ${i}"
    /usr/bin/time mpi_run.py python2 run.py \
    ~/Data/in/nbody/galaxy20m 2> ~/Data/out/20m_cudampi_p3m_${i}
    echo "200m run ${i}"
    /usr/bin/time mpi_run.py python2 run.py\
     ~/Data/in/nbody/galaxy200m 2> ~/Data/out/200m_cudampi_p3m_${i}
    #echo "1b run ${i}"
    #/usr/bin/time mpi_run.py python2 run.py \
     #~/Data/in/nbody/galaxy1b 2> ~/Data/out/1b_cudampi_p3m_${i}
done
