import numpy as np
from larana import lar_utils as laru
from larana import geom
import matplotlib.pyplot as plt
import argparse
from collections import namedtuple
pt = namedtuple("point","x y")

def direct_corr(azimu, ax=[]):
    max_corr = 0.95 * -np.deg2rad(-0.15)

    p0 = pt(-0.1085, 0)
    p1 = pt(-0.4, max_corr)

    m = (p1.y - p0.y) / (p1.x - p0.x)
    b = (p1.x * p0.y - p0.x * p1.y) / (p1.x - p0.x)
    new_azimuth = azimu*m + b
    return new_azimuth



base_dir = '/home/data/uboone/laser/processed/'
laser_filename = base_dir + "laser-data-7267-smooth-calib.npy"
tracks_filename = base_dir + "laser-tracks-7267smooth.npy"

laser_filename = base_dir + "laser-data-23-cross.npy"
tracks_filename = base_dir + "laser-tracks-23-cross.npy"

tracks = np.load(tracks_filename)
lasers = np.load(laser_filename)

# Output options
postfix = ''

for dx in np.linspace(-2,2,21):

    postfix = str(dx)

    # Correction options
    directional = False
    NEW_LASER_POS = [103.53, 9.6, 1080.48]
    NEW_LASER_POS = [102.53, 9.6, 1077.48]
    NEW_LASER_POS = [120 + dx, 0, 1075]
    CORRECTION_AZIMU =  0#-0.34955 #0.020624671357 # * 1.03 #scaling: *1.03
    CORRECTION_POLAR = 0    #-0.55

    # For wire plane cross correction:
    # for 7267: 1) CORRECTION_AZIMU = -0.369780, CORRECTION_POLAR = -0.5
    # for 7252: CORRECTION_AZIMU = -0.34955 CORRECTION_POLAR = -0.55

    # Plotting options
    plot = False
    modulo = 100

    if directional:
        postfix = '-dir'

    lasers_corrected = np.zeros(lasers.shape, dtype=lasers[0].dtype)
    for idx, (laser, track) in enumerate(zip(lasers, tracks)):
        laser_entry, laser_exit, dir, pos, evt = laru.disassemble_laser(laser)
        track_points, levt = laru.disassemble_track(track)
        ldir = np.rec.array([0, 0, 0], dtype=[('x', 'f'), ('y', 'f'), ('z', 'f')])
        lnew_dir = np.rec.array([0, 0, 0], dtype=[('x', 'f'), ('y', 'f'), ('z', 'f')])
        new_dir = np.rec.array([0, 0, 0], dtype=[('x', 'f'), ('y', 'f'), ('z', 'f')])

        ldir.x = -dir.z
        ldir.y = dir.x
        ldir.z = dir.y

        r = 1.
        current_polar = np.arccos(ldir.z/r)
        current_azimuth = np.arctan(ldir.y/ldir.x)

        if directional:
            new_azimuth = current_azimuth + direct_corr(current_azimuth)
            new_polar = current_polar
        else:
            new_azimuth = current_azimuth + np.deg2rad(CORRECTION_AZIMU)
            new_polar = current_polar + np.deg2rad(CORRECTION_POLAR)

        lnew_dir.x = np.sin(new_polar) * np.cos(new_azimuth)
        lnew_dir.y = np.sin(new_polar) * np.sin(new_azimuth)
        lnew_dir.z = np.cos(new_polar)

        new_dir.x = lnew_dir.y
        new_dir.y = lnew_dir.z
        new_dir.z = -lnew_dir.x

        new_entry, new_exit = geom.get_tpc_intersection(NEW_LASER_POS, new_dir.tolist())

        if evt == 42914:
            print(levt)
            current_azimuth = np.arctan(dir.x / dir.z)
            new_azimuth = np.arctan(new_dir.x / new_dir.z)

            z_hit_calib = 136.7
            dz = (z_hit_calib - NEW_LASER_POS[2])
            dx = NEW_LASER_POS[0]
            azimu_calib = np.rad2deg(np.arctan(dx/dz))
            corr = -azimu_calib - np.rad2deg(current_azimuth)
            print('BLAAAAA ' + str(azimu_calib))
            print("BLAAAAA " + str(np.rad2deg(current_azimuth)))
            print("BLAAAAA " + str(np.rad2deg(new_azimuth)))
            print("BLAAAAA " + str(new_exit))
            print('BLAAAAA correction: ' + str(corr))

            fig, ax = laru.make_figure()
            laru.plot_edges(ax, laser_entry.tolist(), laser_exit.tolist(), linestyle='--', color='b', marker='x', alpha=.1)
            laru.plot_edges(ax, new_entry, new_exit, linestyle='--', color='g', marker='x', alpha=.1)
            laru.plot_track(track_points.x, track_points.y, track_points.z, ax, linestyle="", marker="o")

            plt.show()


        lasers_corrected[idx] = (laser[0],
                                 new_entry[0], new_entry[1], new_entry[2],
                                 new_exit[0], new_exit[1], new_exit[2],
                                 new_dir.x, new_dir.y, new_dir.z,
                                 NEW_LASER_POS[0], NEW_LASER_POS[1], NEW_LASER_POS[2])

    # Save the data
    out_file = laser_filename.strip('.npy') + "-calib{}.npy".format(postfix)
    print('write to ', out_file)
    np.save(out_file, lasers_corrected)

    # Some checks / plotting
    if plot:
        fig, ax = laru.make_figure()

    for n, (old, new) in enumerate(zip(lasers, lasers_corrected)):
        if old[0] != new[0]:
            raise ValueError("New index does not match old index!")
        if plot:
            old_entry = [old[1], old[2], old[3]]
            old_exit = [old[4], old[5], old[6]]

            new_entry = [new[1], new[2], new[3]]
            new_exit = [new[4], new[5], new[6]]

            laru.plot_edges(ax, old_entry, old_exit, linestyle='--', color='b', marker='x', alpha=.6)
            laru.plot_edges(ax, new_entry, new_exit, linestyle='--', color='g', marker='o', alpha=.6)

            if n % modulo == 0:
                plt.show()
                fig, ax = laru.make_figure()

    if plot:
        plt.show()