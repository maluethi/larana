import vtk
import numpy as np
from larana.lar_utils import TPC
from collections import namedtuple

LASER_POS = {1: [102.45, 7.60, -31.02],
             2: [101.95, 8.04, 1075.05]}

LASER_RAW_OFFSETS = {1: [0, 0],
                     2: [0, 0]}

# conversion factors for linear encoder: ticks to mm and mm to angle
lin_convert = 0.3499  # conversion from mm to deg
err_convert = 0.0002  # error on coversion from mm to deg
lin_tick = 0.00001  # conversion from tick to mm

def get_tpc_intersection(point, direction, box=None):
    """ Abstract class to calculate the TPC crossings """
    if box is None:
        tpc_box = [TPC.x_min, TPC.x_max, TPC.y_min, TPC.y_max, TPC.z_min, TPC.z_max]
    else:
        tpc_box = box

    t1 = vtk.mutable(0)
    t2 = vtk.mutable(0)

    plane1 = vtk.mutable(0)
    plane2 = vtk.mutable(0)

    entry = [-1., -1., -1.]
    exit = [-1., -1., -1.]

    l = 5000

    ray = [l * direction[0], l*direction[1], l*direction[2]]
    end_point = np.add(point, ray).tolist()

    vtk.vtkBox().IntersectWithLine(tpc_box, point, end_point, t1, t2, entry, exit, plane1, plane2)

    return [entry, exit]

class Laser:
    tup = namedtuple('touple', 'polar, azimu')
    LASER_DEG_OFFSETS = {1: tup(0, 0),  # polar, azimuth
                         2: tup(0, 0)}
    steps_deg = tup(0.000178683, 0.00008064)

    def __init__(self, laser_id):
        self.laser_id = laser_id

    def polar_abs_deg2steps(self, deg):
        if deg > 180 or deg < 0:
            raise ValueError("polar angle is out of boundaries [0, 180], value was " + str(deg))

        return int(1 / self.steps_deg.polar * (deg - self.LASER_DEG_OFFSETS[self.laser_id].polar))

    def polar_deg2steps(self, deg):
        return int(deg / self.steps_deg.polar)

    def azimu_abs_deg2steps(self, deg):
        return int(1 / -self.steps_deg.azimu * (deg - self.LASER_DEG_OFFSETS[self.laser_id].azimu))

    def azimu_deg2steps(self, deg):
        return dir[1] * int(deg / self.steps_deg.azimu)

    def power2steps(self):
        pass