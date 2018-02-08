import numpy as np
from larana import lar_utils as laru
from larana import geom
import matplotlib.pyplot as plt

tracks_filename = "out/laser-tracks-7267.npy"
laser_filename = "out/laser-data-7267.npy"

tracks = np.load(tracks_filename)
lasers = np.load(laser_filename)

NEW_LASER_POS = [102.53, 0, 1077.48]
CORRECTION_AZIMU = 0.
CORRECTION_POLAR = 0.

fig, ax = laru.make_figure()
for idx, (laser, track) in enumerate(zip(lasers, tracks)):
    laser_entry, laser_exit, dir, pos, evt = laru.disassemble_laser(laser)
    current_azimuth = np.arctan(dir.x/dir.z)
    current_polar = np.pi/2 - np.arctan(dir.y/np.sqrt(np.power(dir.z, 2) + np.power(dir.x, 2)))

    plt.plot(evt, np.rad2deg(current_azimuth), 'x')

    new_azimuth = current_azimuth + np.deg2rad(CORRECTION_AZIMU)
    new_polar = current_polar + np.deg2rad(CORRECTION_POLAR)

    new_x = 1.0 * np.sign(dir.x)
    new_z = new_x / np.tan(new_azimuth)
    new_y = - np.tan(new_polar - np.pi/2) * np.sqrt(np.power(new_z,2) + np.power(new_x,2))

    l = np.sqrt(np.sum([np.power(e,2) for e in [new_x, new_y, new_z]]))
    new_x /= l
    new_y /= l
    new_z /= l

    en, ex = geom.get_tpc_intersection(NEW_LASER_POS, [new_x, new_y, new_z])

    print([new_x, new_y, new_z], dir)

    print(dir.x - new_x)

    laru.plot_edges(ax, en, ex, linestyle='--', color='b', marker='x', alpha=.1)
    laru.plot_edges(ax, laser_entry.tolist(), laser_exit.tolist(), linestyle='--', color='g', marker='x', alpha=.1)

    if idx % 100 == 0:
        plt.show()
        fig, ax = laru.make_figure()

plt.show()

