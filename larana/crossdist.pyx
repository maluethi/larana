cimport cython
from libc.math cimport pow, sqrt

@cython.boundscheck(False)
@cython.wraparound(False)
cpdef closest_dist(double[:,:] track, double[:] pt, double[:] out):
    cdef double dx, dy, dz = 0.
    cdef double d = 9990.
    cdef int idx = -1

    for i in range(track.shape[1]):
        dx = pow(track[0, i] - pt[0],2)
        dy = pow(track[1, i] - pt[1],2)
        dz = pow(track[2, i] - pt[2],2)
        d_new = sqrt(dx + dy + dz)
        if d_new < d:
            d = d_new
            idx = i

    out[0] = d
    out[1:4] = pt
    out[4:7] = track[:,idx]