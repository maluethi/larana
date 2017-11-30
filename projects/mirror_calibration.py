from larana.lar_utils import read_tracks, read_laser, disassemble_laser, disassemble_track, close_to_side
from larana.geom import TPC, Point, Ring, Line

from matplotlib.collections import PatchCollection, LineCollection
from matplotlib.patches import Circle, Rectangle

import matplotlib.pyplot as plt
import numpy as np

from scipy.optimize import minimize
from functools import partial

def calc_widths(filename, n_bins=1000):
    tracks = read_tracks(filename)
    lasers = read_laser(filename)

    # generate event id lists, since there are more tracks than events
    track_event_id = np.array([track[0] for track in tracks])

    azimu = []

    # loop over all tracks in the file
    for laser in lasers:
        _, _, dir, _, evt = disassemble_laser(laser)
        track_list = np.where(track_event_id == evt)

        # loop over all tracks in this event
        for track in tracks[track_list]:
            track_points, evt = disassemble_track(track)
            if close_to_side(track_points, 10., 2):
                azimu.append(np.rad2deg(np.arctan(dir.x / dir.z)))

    entries, bins,  = np.histogram(azimu, n_bins)
    return bins, entries

def tangent_angles(laser_pos, rings):
    angles = [np.rad2deg(ring.tangent(laser_pos))for ring in rings]
    return angles


def viewable_angles(angles):
    pass


def opening_angle(angles):
    opening_angles = []
    opening = []
    for idx in range(1, len(angles)):
        delta = angles[idx][0] - angles[idx-1][1]
        if delta > 0.:
            opening_angles.append([angles[idx-1][1], angles[idx][0]])
            opening.append(delta)


    return opening_angles, opening


def plot_rings(ax, rings):
    circles = []
    for ring in rings:
        circles.append(Circle([ring.center.x, ring.center.y], ring.radius))
    ring_collection = PatchCollection(circles)
    ax.add_collection(ring_collection)


def plot_tangents(ax, angles, laser_pos):
    lines = []
    for angle in angles:
        line_low = Line(laser_pos, angle[0])
        line_hig = Line(laser_pos, angle[1])
        lines.append([[laser_pos.x, laser_pos.y], [5, line_low.at(5)]])
        lines.append([[laser_pos.x, laser_pos.y], [5, line_hig.at(5)]])

    line_collection = LineCollection(lines)
    ax.add_collection(line_collection)

def get_edges(bins, entries, threshold, width_bin=10.):
    over = False
    edges = []
    for idx in range(1, len(entries)):
        if entries[idx] > threshold and not over:
            start = bins[idx]
            start_idx = idx
            over = True
        elif entries[idx] < threshold and over:
            end = bins[idx]
            if idx - start_idx > width_bin:
                edges.append([start, end])
            over = False

    widths = [edge[1] - edge[0] for edge in edges]
    return edges, widths

def iterate(laser_pos, edgs=None, wid=None, plotting=False):
    laser_pos = Point(laser_pos[0], laser_pos[1])
    ring_radius = 1.25
    rings = [Ring(Point(0, z), ring_radius) for z in np.arange(-18, 6, 4)]

    angles = tangent_angles(laser_pos, rings)
    op_angles, opening = opening_angle(angles)

    res = 0
    weights = [0.2, 0.2, 1., 1, 1.5]
    for width, op, edg, op_ang, w in zip(wid, opening, edgs, op_angles, weights):
        res_wid = np.abs(edg[1] - op_ang[1])
        res_edg = np.abs(edg[0] - op_ang[0])

        print("edg:", edg[0],op_ang[0])

        print("res", res_wid, res_edg)
        res += w*(res_wid + res_edg)

    # plotting
    if plotting:
        fig2, ax2 = plt.subplots()

        for angle, op in zip(op_angles, opening):
            rect = Rectangle([angle[0], 0], op, 5.0, fill='red', alpha=0.5)
            ax2.add_patch(rect)
        plt.xlim([-45, 5])

        plt.plot(bins[:-1], entries)

        for edg, op_ang in zip(edgs, op_angles):
            plt.axvline(x=edg[0], color='red', alpha=0.3)
            plt.axvline(x=edg[1], color='red', alpha=0.3)
            plt.axvline(x=op_ang[0], color='green', alpha=0.3)
            plt.axvline(x=op_ang[1], color='green', alpha=0.3)
        plt.show()
    print("-------------",res,"------------")
    print(laser_pos)
    return res

gen_histo = False
n_bins = 1000
hist_file = "./out/histo_calib/histo_{}.npy".format(n_bins)
if gen_histo:
    track_file = "/home/data/uboone/laser/7267/tracks/Tracks-7267-roi.root"
    bins, entries = calc_widths(track_file, n_bins)
    np.save(hist_file, [bins, entries])
else:
    bins, entries = np.load(hist_file)

edges, widths = get_edges(bins, entries, 3.)

laser_pos = [-36, -0.5]
iter = partial(iterate, edgs=edges, wid=widths)
res = minimize(iter, laser_pos, bounds=[(-50, -1), [-2, 2]],method='nelder-mead', options={'xtol': 1e-8, 'disp': True})
print(res)




fig2, ax2 = plt.subplots()

laser_pos = Point(res.x[0], res.x[1])
ring_radius = 1.25
rings = [Ring(Point(0, z), ring_radius) for z in np.arange(-18, 6, 4)]

angles = tangent_angles(laser_pos, rings)
op_angles, opening = opening_angle(angles)


for angle, op in zip(op_angles, opening):
    rect = Rectangle([angle[0], 0], op, 15.0, fill='red', alpha=0.5)
    ax2.add_patch(rect)
plt.xlim([-30, 5])
plt.ylim([0,20])

plt.plot(bins[:-1], entries)

for lin, op_ang in zip(edges, op_angles):
    plt.axvline(x=lin[0], color='red', alpha=0.3)
    plt.axvline(x=lin[1], color='red', alpha=0.3)
    plt.axvline(x=op_ang[0], color='green', alpha=0.3)
    plt.axvline(x=op_ang[1], color='green', alpha=0.3)
plt.show()

fig1, ax = plt.subplots()
plot_rings(ax, rings)
plot_tangents(ax, op_angles, laser_pos)
ax.plot(laser_pos.x, laser_pos.y, "x")
ax.set_aspect(1)
plt.show()

