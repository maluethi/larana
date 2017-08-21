from larana.lar_utils import TPC
from larana.geom import LASER_POS, get_tpc_intersection
import numpy as np

from collections import namedtuple

def generate_span(laser_id, azimu_start, azimu_end, azimu_steps, polar_start, polar_end, polar_steps):
    azimu_steps = list(np.linspace(azimu_start, azimu_end, azimu_steps))
    polar_steps = list(np.linspace(polar_start, polar_end, polar_steps))

    mesh_input = np.meshgrid(azimu_steps, polar_steps, [1.])

    it = np.nditer(mesh_input, flags=['multi_index'])
    shots_input = []
    while not it.finished:
        values = np.hstack([it[0], it[1], it[2]])
        shots_input.append(values.tolist())
        it.iternext()

    return shots_input


def convert_to_uboone(azimu, polar, r, laser_id):
    z_invert = {1: 1,
                2: -1}

    pol, azi = np.deg2rad(polar), np.deg2rad(azimu)

    x = r * np.sin(pol) * np.cos(azi)
    y = r * np.sin(pol) * np.sin(azi)
    z = r * np.cos(pol)

    ub_x = z
    ub_y = y
    ub_z = x * z_invert[laser_id]

    return [ub_x, ub_y, ub_z]


def gen_textfile(filename, entry_points, directions, momentum=10):
    fields = ["status", "pdg", "fst_mother", "scd_mother", "fst_daughter", "scd_daugther", "px", "py", "pz", "E", "x",
              "y", "z", "t"]
    defaults = (1, 13, 0, 0, 0, 0, 0, 0, 0, 10., 0, 0, 0, 0)
    mc_info = namedtuple("mc", fields)
    mc_info.__new__.__defaults__ = defaults

    forma = 6 * "{} " + 8 * " {:0.5f}"

    with open(filename, "w+") as f:
        for evt, (direc, entry) in enumerate(zip(directions, entry_points)):
            mc = mc_info(x=entry[0],
                         y=entry[1],
                         z=entry[2],
                         px=direc[0] * momentum,
                         py=direc[1] * momentum,
                         pz=direc[2] * momentum
                         )
            values = mc._asdict().values()

            f.write(str(evt) + ' 1\n')
            f.write(forma.format(*values) + "\n")









