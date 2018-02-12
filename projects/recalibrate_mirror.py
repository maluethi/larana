import numpy as np
from larana import lar_utils as laru
from larana import geom
import matplotlib.pyplot as plt

tracks_filename = "out/laser-tracks-7267.npy"
laser_filename = "out/laser-data-7267.npy"

tracks = np.load(tracks_filename)
lasers = np.load(laser_filename)

NEW_LASER_POS = [102.53, 7.6, 1077.48]
CORRECTION_AZIMU = 2.
CORRECTION_POLAR = 0.



#fig, ax = laru.make_figure()
for idx, (laser, track) in enumerate(zip(lasers, tracks)):
    laser_entry, laser_exit, dir, pos, evt = laru.disassemble_laser(laser)
    current_azimuth = np.arctan(dir.x/dir.z)
    current_polar = np.pi/2 - np.arctan(dir.y/np.sqrt(np.power(dir.z, 2) + np.power(dir.x, 2)))

    #plt.plot(evt, np.rad2deg(current_azimuth), 'x')

    new_azimuth = current_azimuth + np.deg2rad(CORRECTION_AZIMU)
    new_polar = current_polar + np.deg2rad(CORRECTION_POLAR)

    new_laser_dir = np.rec.array([laser['dir.x()'],
                              laser['dir.y()'],
                              laser['dir.z()']],
                             dtype=[('x', 'f'), ('y', 'f'), ('z', 'f')])

    new_laser_dir.x = 1.0 * np.sign(dir.x)
    new_laser_dir.z = new_laser_dir.x / np.tan(new_azimuth)
    new_laser_dir.y = - np.tan(new_polar - np.pi/2) * np.sqrt(np.power(new_laser_dir.z,2) + np.power(new_laser_dir.x,2))

    l = np.sqrt( np.sum(np.power(new_laser_dir.tolist(), 2)))
    new_laser_dir.x /= l
    new_laser_dir.y /= l
    new_laser_dir.z /= l

    en, ex = geom.get_tpc_intersection(NEW_LASER_POS, new_laser_dir.tolist())

    #print(new_laser_dir, dir)

    #print(dir.x - new_laser_dir.x)

    #laru.plot_edges(ax, en, ex, linestyle='--', color='b', marker='x', alpha=.1)
    #laru.plot_edges(ax, laser_entry.tolist(), laser_exit.tolist(), linestyle='--', color='g', marker='x', alpha=.1)

    if evt % 100000== 0:
        plt.show()
        fig, ax = laru.make_figure()

#plt.show()

