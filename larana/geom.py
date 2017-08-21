import vtk
import numpy as np
from larana.lar_utils import TPC

LASER_POS = {1: [103, 7.6, -30],
             2: [103., 7.6, 1073.1]}

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