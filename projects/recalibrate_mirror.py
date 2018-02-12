import numpy as np
from larana import lar_utils as laru
from larana import geom
import matplotlib.pyplot as plt

base_dir = '/home/data/uboone/laser/processed/'
laser_filename = base_dir + "laser-data-7267.npy"

#tracks = np.load(tracks_filename)
lasers = np.load(laser_filename)

# Output options
postfix = ''

# Correction options
NEW_LASER_POS = [102.53, 7.6, 1077.48]
CORRECTION_AZIMU = 2.
CORRECTION_POLAR = 0.

# Plotting options
plot = False
modulo = 100

lasers_corrected = np.zeros(lasers.shape, dtype=lasers[0].dtype)
for idx, laser in enumerate(lasers):
    laser_entry, laser_exit, dir, pos, evt = laru.disassemble_laser(laser)
    current_azimuth = np.arctan(dir.x/dir.z)
    current_polar = np.pi/2 - np.arctan(dir.y/np.sqrt(np.power(dir.z, 2) + np.power(dir.x, 2)))

    new_azimuth = current_azimuth + np.deg2rad(CORRECTION_AZIMU)
    new_polar = current_polar + np.deg2rad(CORRECTION_POLAR)

    new_dir = np.rec.array([laser['dir.x()'],
                            laser['dir.y()'],
                            laser['dir.z()']],
                           dtype=[('x', 'f'), ('y', 'f'), ('z', 'f')])

    new_dir.x = 1.0 * np.sign(dir.x)
    new_dir.z = new_dir.x / np.tan(new_azimuth)
    new_dir.y = - np.tan(new_polar - np.pi / 2) * np.sqrt(np.power(new_dir.z, 2) + np.power(new_dir.x, 2))

    l = np.sqrt(np.sum(np.power(new_dir.tolist(), 2)))
    new_dir.x /= l
    new_dir.y /= l
    new_dir.z /= l

    new_entry, new_exit = geom.get_tpc_intersection(NEW_LASER_POS, new_dir.tolist())

    lasers_corrected[idx] = (laser[0],
                             new_entry[0], new_entry[1], new_entry[2],
                             new_exit[0], new_exit[1], new_exit[2],
                             new_dir.x, new_dir.y, new_dir.z,
                             NEW_LASER_POS[0], NEW_LASER_POS[1], NEW_LASER_POS[2])

# Save the data
out_file = laser_filename.strip('.npy') + "-calib{}.npy".format(postfix)
print('write to', out_file)
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

        laru.plot_edges(ax, old_entry, old_exit, linestyle='--', color='b', marker='x', alpha=.1)
        laru.plot_edges(ax, new_entry, new_exit, linestyle='--', color='g', marker='x', alpha=.1)

        if n % modulo == 0:
            plt.show()
            fig, ax = laru.make_figure()

if plot:
    plt.show()