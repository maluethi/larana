from larana import geom
from larana import lar_utils as laru
import numpy as np
import matplotlib.pyplot as plt
from larana.crossdist import closest_dist

import pickle

def closest_point(pt, track):
    x, y, z = track[1], track[2], track[3]
    dx = np.power(x - pt[0], 2)
    dy = np.power(y - pt[1], 2)
    dz = np.power(z - pt[2], 2)

    d = np.sqrt(dx + dy + dz)
    min_d = np.min(d)
    min_arg = np.argmin(d)

    return [min_d, x[min_arg], y[min_arg], z[min_arg], pt[0], pt[1], pt[2]]

def c_closest_distance(track1, track2):
    pts = np.column_stack((track1[1],track1[2],track1[3]))
    track2 = np.array([track2[1], track2[2], track2[3]], dtype=float)

    d = np.zeros((len(pts), 7))
    for i, pt in enumerate(pts):
        pt = np.array(pt, dtype=np.double)
        di = np.zeros(7)
        closest_dist(track2, pt, di)
        d[i] = di

    min_idx = np.argmin(d[:, 0])
    min_d = d[min_idx][0]
    min_pt1 = d[min_idx][4:7]
    min_pt2 = d[min_idx][1:4]

    del d

    return min_d, min_pt1, min_pt2

def closest_distance(track1, track2):
    pts = np.column_stack((track1[1],track1[2],track1[3]))

    d = np.array([closest_point(pt, track2) for pt in pts])

    min_idx = np.argmin(d[:, 0])
    min_d = d[min_idx][0]
    min_pt1 = d[min_idx][4:7]
    min_pt2 = d[min_idx][1:4]

    return min_d, min_pt1, min_pt2

base_dir = '/home/data/uboone/laser/processed/'
laser_file1 = base_dir + "laser-data-31-cross.npy"
track_file1 = base_dir + "laser-tracks-31-cross.npy"
laser_file2 = base_dir + "laser-data-23-cross.npy"
track_file2 = base_dir + "laser-tracks-23-cross.npy"


stride = 1

laser1 = np.load(laser_file1)[::stride]
laser2 = np.load(laser_file2)[::stride]
track1 = np.load(track_file1)[::stride]
track2 = np.load(track_file2)[::stride]

plot = False


cross = []
for idx1, (l1, t1) in enumerate(zip(laser1, track1)):
    l1_entry, l1_exit, _, _, evt1 = laru.disassemble_laser(l1)
    print('tr1: {} / {}'.format(idx1, len(laser1)))
    for idx2, (l2, t2) in enumerate(zip(laser2, track2)):
        l2_entry, l2_exit, _, _, evt2 = laru.disassemble_laser(l2)
        d, p, m = geom.get_closest_distance(l1_entry.tolist(), l1_exit.tolist(),
                                            l2_entry.tolist(), l2_exit.tolist())

        # print(evt1,evt2,d, p, m)
        if d > 10.:
            continue

        min_d, pt1, pt2 = c_closest_distance(t1, t2)

        if min_d < 25.:

            cross.append([idx1, idx2, [d, p, m], [min_d, pt1, pt2]])
            if plot:
                x1, y1, z1 = t1[1], t1[2], t1[3]
                x2, y2, z2 = t2[1], t2[2], t2[3]
                fig, ax = laru.make_figure()

                laru.plot_track(x1, y1, z1, ax, **{'color': 'r', 'marker': 'o'})
                laru.plot_track(x2, y2, z2, ax, **{'color': 'b', 'marker': 'o'})

                laru.plot_edges(ax, l1_entry.tolist(), l1_exit.tolist())
                laru.plot_edges(ax, l2_entry.tolist(), l2_exit.tolist())
                laru.plot_edges(ax, p, m)
                laru.plot_edges(ax, pt1, pt2)
                plt.show()

with open("./out/cross-reco.txt", "wb+") as fp:
    pickle.dump(cross, fp)