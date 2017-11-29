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
    tup = namedtuple('tuple', 'polar, azimu')

    steps_deg = tup(0.000178683, 0.00008064)

    _polar_tick_length = 0.00001
    _polar_linear2deg = 0.3499  # mm/deg

    # for now (LCS2):
    _z_observed = 171.5 # TODO: Make this more accurate and get error
    _y_observed = 6.1   # TODO: Make this more accurate and get error
    _lcs2_azimu_apparent_angle = 155.46600348
    _lcs2_azimu_true_ange = np.rad2deg(np.tan(LASER_POS[2][0] / (LASER_POS[2][2] - _z_observed)))

    _lcs2_polar_true_angle = 90.0 - np.rad2deg(np.tan(_y_observed / (LASER_POS[2][2] - _z_observed)))
    _lcs2_polar_apparent_ticks = 10402809
    _lcs2_polar_apparent = _polar_tick_length * _lcs2_polar_apparent_ticks / _polar_linear2deg

    _lcs1_azimu_true_angle = 0.
    _lcs2_polar_calib = 0.

    LASER_DIR = {1: tup(1, 1),
                 2: tup(1, 1)}

    LASER_DEG_OFFSETS = {1: tup(_lcs2_polar_calib, _lcs1_azimu_true_angle),  # polar, azimuth
                         2: tup((_lcs2_polar_apparent - _lcs2_polar_true_angle),
                                (_lcs2_azimu_apparent_angle + _lcs2_azimu_true_ange))}

    def __init__(self, laser_id):
        self.laser_id = laser_id
        self.pos = LASER_POS[laser_id]

        self.laser_deg_offset = self.LASER_DEG_OFFSETS[laser_id]
        self.laser_dir = self.LASER_DIR[laser_id]

    def polar_tick2laser(self, tick):
        raw = self.polar_tick2raw(tick)
        return self.polar_raw2laser(raw)

    def polar_laser2tick(self, laser):
        raw = self.polar_laser2raw(laser)
        return self.polar_raw2tick(raw)

    def laser2raw(self, polar, azimu):
        """ Converts angles seen in laser coordinates into raw coordinates """
        return [self.polar_laser2raw(polar), self.azimu_laser2raw(azimu)]

    def azimu_laser2raw(self, deg):
        raw = self.laser_dir.azimu * deg + self.laser_deg_offset.azimu
        return raw

    def azimu_raw2laser(self, raw):
        deg = (raw - self.laser_deg_offset.azimu) / self.laser_dir.azimu
        return deg

    def polar_laser2raw(self, deg):
        raw = self.laser_dir.polar * deg + self.laser_deg_offset.polar
        return raw

    def polar_raw2laser(self, raw):
        laser = (raw - self.laser_deg_offset.polar) / self.laser_dir.polar
        return laser

    def azimu_raw2ticks(self, deg):
        pass

    def polar_tick2raw(self, tick):
        deg = tick * self._polar_tick_length / self._polar_linear2deg
        return deg

    def polar_raw2tick(self, raw):
        tick = raw * self._polar_linear2deg / self._polar_tick_length
        return int(tick)

    def azimu_deg2steps(self, deg):
        return int(deg / self.steps_deg.azimu)

    def power2steps(self):
        pass


def angle(pt1, pt2):
    return pt1.angle(pt2)


def dist(pt1, pt2):
    return pt1.dist(pt2)


class Point():
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        if isinstance(other, Point):
            self.x += other.x
            self.y += other.y
        else:
            raise ValueError('not point')

    def dist(self, other):
        dx = np.abs(self.x - other.x)
        dy = np.abs(self.y - other.y)
        d = np.sqrt(np.power(dx,2) + np.power(dy,2))
        return d

    def angle(self, other):
        dx = np.abs(self.x - other.x)
        dy = np.abs(self.y - other.y)
        a = np.arctan(dy/dx)
        return a

class Ring():
    def __init__(self, center, radius):
        self.center = center
        self.radius = radius

    def tangent(self, point):
        d = dist(self.center, point)
        ang = angle(self.center, point)
        tangent_angle = np.arcsin(self.radius/d)

        return [ang - tangent_angle, ang + tangent_angle]