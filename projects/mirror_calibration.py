from larana.lar_utils import read_tracks, read_laser, disassemble_laser, disassemble_track, close_to_side
from larana.geom import TPC, Point, Ring, Line

from matplotlib.collections import PatchCollection, LineCollection
from matplotlib.patches import Circle, Rectangle

import matplotlib.pyplot as plt
import numpy as np

def calc_widths(filename):
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

    entries, bins,  = np.histogram(azimu, 1000)
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


gen_histo = False
hist_file = "./out/histo_calib/histo_1000.npy"
if gen_histo:
    filename = "/home/data/uboone/laser/7267/tracks/Tracks-7267-roi.root"
    bins, entries = calc_widths(filename)
    np.save(hist_file, [bins, entries])
else:
    bins, entries = np.load(hist_file)

laser_pos = Point(-36, 1.6)
ring_radius = 1.25
rings = [Ring(Point(0, z), ring_radius) for z in np.arange(-28, 29, 4)]

angles = tangent_angles(laser_pos, rings)
op_angles, opening = opening_angle(angles)

fig1, ax = plt.subplots()
plot_rings(ax, rings)
plot_tangents(ax, op_angles, laser_pos)
ax.plot(laser_pos.x, laser_pos.y, "x")
ax.set_aspect(1)
plt.show()

fig2, ax2 = plt.subplots()
for angle, op in zip(op_angles, opening):
    print(angle[0], op)

    rect = Rectangle([angle[0], 0], op, 5.0, fill='red', alpha=0.5)
    ax2.add_patch(rect)
plt.xlim([-50,50])

plt.plot(bins[:-1], entries)

plt.show()




