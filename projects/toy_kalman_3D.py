import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle, FancyBboxPatch

from filterpy.kalman import KalmanFilter
from filterpy.common import Q_discrete_white_noise

def gen_track(start, end, stepsize=(0.3, 0.3)):
    """ Generates  track as seen in a tpc with wirespaceing 0.3mm from start to end position"""

    wire_z = np.arange(start[0], end[0], step=stepsize[0])
    wire_y = np.arange(start[1], end[1], step=stepsize[1])

    if len(wire_z) == 0:
        wire_z = np.array([start[0]]*len(wire_y))
    if len(wire_y) == 0:
        wire_y = np.array([start[1]]*len(wire_z))

    return wire_z, wire_y


kf = KalmanFilter(dim_x=4, dim_z=2)

dz = 0.3

kf.x = np.array([1., 1.])

kf.R = 2
kf.F = np.array([[1., dz, 0., 0.],
                 [0., 1., 0., 0.],
                 [0., 0., 1., dz],
                 [0., 0., 0., 1.]])

kf.H = np.array([[1., 0., 0., 0.],
                 [0., 0., 1., 0.]])
kf.P *= [5., 2., 5., 2.]
q = Q_discrete_white_noise(2, dz, var=2.)
kf.Q = np.diag([q,q])