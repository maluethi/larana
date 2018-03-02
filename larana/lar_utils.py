import root_numpy as rn
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import matplotlib.patches as patches
from matplotlib import gridspec

import ROOT

import logging
import time

import types
from collections import namedtuple

import matplotlib.cm as cm

cmap = cm.rainbow(np.linspace(0, 1, 500))
TPC_LIMITS = [[0, 256], [-116.38, 116.38], [0, 1036.8]]
box = namedtuple("box", "x_min x_max y_min y_max z_min z_max")

TPC = box(TPC_LIMITS[0][0], TPC_LIMITS[0][1], TPC_LIMITS[1][0], TPC_LIMITS[1][1], TPC_LIMITS[2][0], TPC_LIMITS[2][1])
WIRE = box(0, 256, -115.505, 117.153, 0.0, 1036.45)

def correct(track):
    return 'track {} is ok'.format(track)


def load_tracks(file):
    return [0, 1, 2, 3, 4, 5]


# Plotting
def plot_track(x, y, z, axes, **kwargs):
    ax_zx, ax_zy, ax_xy = axes

    zx_sc = ax_zx.plot(z, x, **kwargs)
    zy_sc = ax_zy.plot(z, y, **kwargs)
    xy_sc = ax_xy.plot(x, y, **kwargs)

    return [zx_sc, zy_sc, xy_sc]


def plot_edges(axes, start, end, **kwargs):
    if kwargs is None:
        axes[0].plot([start[2], end[2]], [start[0], end[0]], '-*')
        axes[1].plot([start[2], end[2]], [start[1], end[1]], '-*')
        axes[2].plot([start[0], end[0]], [start[1], end[1]], '-*')
    else:
        axes[0].plot([start[2], end[2]], [start[0], end[0]], **kwargs)
        axes[1].plot([start[2], end[2]], [start[1], end[1]], **kwargs)
        axes[2].plot([start[0], end[0]], [start[1], end[1]], **kwargs)


def plot_point(axes, pt):
    x, y, z = pt
    axes[0].plot(z, x, 'o')
    axes[1].plot(z, y, 'o')
    axes[2].plot(x, y, 'o')


def plot_endpoints(x, y, z, axes, laser=[], **kwargs):
    ax_zx, ax_zy, ax_xy = axes

    furthest = np.argmax(z)
    closest = np.argmin(z)

    last_point = [el[furthest] for el in [x,y,z]]
    first_point = [el[closest] for el in [x,y,z]]

    if not laser:
        ax_zx.plot([z[closest], z[furthest]], [x[closest], x[furthest]], "-*")
        ax_zy.plot([z[closest], z[furthest]], [y[closest], y[furthest]], "-*")
        ax_xy.plot([x[closest], x[furthest]], [y[closest], y[furthest]], "-*")
    if laser:
        laser_entry, laser_exit = laser
        ax_zx.plot([z[closest], laser_exit.z], [x[closest], laser_exit.x], '-o', markevery=2, markersize=2, linewidth=0.3, alpha=0.6)
        ax_zy.plot([z[closest], laser_exit.z], [y[closest], laser_exit.y], '-o', markevery=2, markersize=2, linewidth=0.3, alpha=0.6)
        ax_xy.plot([x[closest], laser_exit.x], [y[closest], laser_exit.y], '-o', markevery=2, markersize=2, linewidth=0.3, alpha=0.6)

        if not in_tpc(first_point):
            print("outside")


def plot_lines(lines, axes, colors=None):
    """ this is plotting each line collection on the respective axes, so both arguments should have the
     same size. """
    if lines is None:
        return
    if colors is not None:
        colors = [cmap[col] for col in colors]

    for line_collection, ax in zip(lines, axes):
        ax.add_collection(LineCollection(line_collection, linewidths=1, linestyles='solid', colors=colors))


def assemble_lines(laser_data):
    zx_laser_lines = []
    zy_laser_lines = []
    xy_laser_lines = []

    for laser in laser_data:
        laser_entry = np.rec.array([laser[1], laser[2], laser[3]],
                                   dtype=[('x', 'f'), ('y', 'f'), ('z', 'f')])
        laser_exit = np.rec.array([laser[4], laser[5], laser[6]],
                                  dtype=[('x', 'f'), ('y', 'f'), ('z', 'f')])

        zx_laser_lines.append([(laser_entry.z, laser_entry.x), (laser_exit.z, laser_exit.x)])
        zy_laser_lines.append([(laser_entry.z, laser_entry.y), (laser_exit.z, laser_exit.y)])
        xy_laser_lines.append([(laser_entry.x, laser_entry.y), (laser_exit.x, laser_exit.y)])

    return [zx_laser_lines, zy_laser_lines, xy_laser_lines]

def assemble_line(laser_entry, laser_exit):

    laser_entry = laser_entry.tolist()
    laser_exit = laser_exit.tolist()

    laser_df = [0,
                  laser_entry[0],
                  laser_entry[1],
                  laser_entry[2],
                  laser_exit[0],
                  laser_exit[1],
                  laser_exit[2]]
    return assemble_lines([laser_df])


def make_figure(tpc_limits=True, tpc_box=False, link_axes=True):
    fig = plt.figure(figsize=(8, 5.), dpi=160)

    gs = gridspec.GridSpec(3, 3)

    ax_zx = fig.add_subplot(gs[0, :])

    if link_axes:
        ax_zy = fig.add_subplot(gs[1, :], sharex=ax_zx)
        ax_xy = fig.add_subplot(gs[2, 0], sharey=ax_zy)
    else:
        ax_zy = fig.add_subplot(gs[1, :])
        ax_xy = fig.add_subplot(gs[2, 0])


    axes = [ax_zx, ax_zy, ax_xy]
    if tpc_limits:
        set_tpc_limits(axes)

    if tpc_box:
        plot_tpc_box(axes)

    if link_axes:
        ax_xy.update_xlim = types.MethodType(sync_y_with_x, ax_xy)
        ax_zy.update_ylim = types.MethodType(sync_x_with_y, ax_zx)

        ax_zx.callbacks.connect("ylim_changed", ax_xy.update_xlim)
        ax_xy.callbacks.connect("xlim_changed", ax_zy.update_ylim)

    return fig, axes


def set_tpc_limits(axes):
    ax_zx, ax_zy, ax_xy = axes

    ax_zx.set_xlim([0, 1036.8])
    ax_zx.set_ylim([0, 256.])
    ax_zx.set_xlabel("z [cm]")
    ax_zx.set_ylabel("x [cm]")

    ax_zy.set_xlim([0, 1036.8])
    ax_zy.set_ylim([-116., 116.])
    ax_zy.set_xlabel("z [cm]")
    ax_zy.set_ylabel("y [cm]")

    ax_xy.set_xlim([0, 256])
    ax_xy.set_ylim([-116., 116.])
    ax_xy.set_xlabel("x [cm]")
    ax_xy.set_ylabel("y [cm]")


def plot_tpc_box(axes):
    ax_zx, ax_zy, ax_xy = axes

    box_style = {"alpha":1, "linestyle":"solid", "facecolor": None, "edgecolor":"b", "fill":False}

    zx_patch = patches.Rectangle((0,0), TPC_LIMITS[2][1], TPC_LIMITS[0][1], **box_style)
    zy_patch = patches.Rectangle((0,TPC_LIMITS[1][0]), TPC_LIMITS[2][1], 2*TPC_LIMITS[1][1], **box_style)
    xy_patch = patches.Rectangle((0,TPC_LIMITS[1][0]), TPC_LIMITS[0][1], 2*TPC_LIMITS[1][1], **box_style)

    ax_zx.add_patch(zx_patch)
    ax_zy.add_patch(zy_patch)
    ax_xy.add_patch(xy_patch)


def sync_y_with_x(self, event):
    self.set_xlim(event.get_ylim(), emit=False)


def sync_x_with_y(self, event):
    self.set_ylim(event.get_xlim(), emit=False)


def calc_line(point1, point2):
    """ Calculate the two parameters of a line base on the two supplied points """
    m = (point2[1] - point1[1]) / (point2[0] - point1[0])
    b = point1[1] - m * point1[0]
    return m, b


def calc_line_slope(point, slope):
    """ Calculate two parameters of a line based on a point and its slope """
    b = point[1] - slope * point[0]
    return slope, b


def calc_intersect(m1, b1, m2, b2):
    x = (b2 - b1) / (m1 - m2)
    y = m1 * x + b1
    return [x, y]


def calc_distance(point1, point2):
    return np.sqrt(np.power(np.abs(point1[0] - point2[0]), 2) + np.power(np.abs(point1[1] - point2[1]), 2))


def close_to_side(track, region_z, laser_id):
    if laser_id == 1:
        min_z = np.min(track.z)
        if np.abs(TPC.z_min - min_z) < region_z:
            return True
    elif laser_id == 2:
        max_z = np.max(track.z)
        if np.abs(TPC.z_max - max_z) < region_z:
            return True
    return False

def endpoint_inside(laser_track):
    x, y, z = laser_track

    closest = np.argmin(z)
    first_point = [el[closest] for el in [x, y, z]]
    return in_tpc(first_point)


def in_tpc(point, ignore_x=True):
    x, y, z = point

    if not ignore_x and (x > TPC.x_max or x < TPC.x_min):
        return False
    elif y > TPC.y_max or y < TPC.y_min:
        return False
    elif z > TPC.z_max or z < TPC.z_min:
        return False
    else:
        return True


# reading
def find_tree(tree_to_look_for, filename):
    """ Find argument tree name that contains Track Information """
    trees = rn.list_trees(filename)
    try:
        track_tree = next(tree for tree in trees if tree_to_look_for.lower() in tree.lower())
    except StopIteration:
        raise ValueError("No tree with name \"" + tree_to_look_for + "\" found in file")

    return track_tree


def get_branches(filename: object, treename: object, vectors: object = None) -> object:
    """ function that returns the appropriate branch string in a branch for the specified vectors of the branch  """
    if vectors is None:
        return rn.list_branches(filename, treename=treename)

    all_branches = rn.list_branches(filename, treename=treename)

    for vector in vectors:
        try:
            all_branches.pop(all_branches.index(vector))
        except:
            continue

        all_branches.extend([vector + '.x()', vector + '.y()', vector + '.z()'])

    return all_branches


def read_laser(filename, identifier='Laser'):
    laser_tree = find_tree(identifier, filename)
    laser_branches = get_branches(filename, laser_tree, vectors=['dir', 'pos'])
    laser_data = rn.root2array(filename, treename=laser_tree, branches=laser_branches)
    return laser_data


def read_tracks(filename, identifier='Tracks'):
    track_data = rn.root2array(filename, treename=find_tree(identifier, filename))
    return track_data

def read_raw(filename, identifier='Raw'):
    raw_data = rn.root2array(filename, treename=find_tree(identifier, filename))
    return raw_data

def read_data(filename):
    return read_tracks(filename), read_laser(filename)


def disassemble_track(track):
    event_id = track[0]
    track = np.rec.array([track[1], track[2], track[3]],
                         dtype=[('x', 'f'), ('y', 'f'), ('z', 'f')])
    return track, event_id


def disassemble_laser(laser):
    event = laser[0]
    laser_entry = np.rec.array([laser[1], laser[2], laser[3]],
                               dtype=[('x', 'f'), ('y', 'f'), ('z', 'f')])
    laser_exit = np.rec.array([laser[4], laser[5], laser[6]],
                              dtype=[('x', 'f'), ('y', 'f'), ('z', 'f')])

    laser_dir = np.rec.array([laser[7], laser[8], laser[9]],
                             dtype=[('x', 'f'), ('y', 'f'), ('z', 'f')])

    laser_pos = np.rec.array([laser[10], laser[11], laser[12]],
                             dtype=[('x', 'f'), ('y', 'f'), ('z', 'f')])

    return laser_entry, laser_exit, laser_dir, laser_pos, event


def write_to_root(tracks, laser):
    """ Writes tracks and laser data to a root file which is readable by the reconstruction algorithm """
    from rootpy.vector import Vector3
    import rootpy.stl as stl

    from rootpy.tree import Tree
    from rootpy.io import root_open

    laser_entry, laser_exit = laser

    Vec = stl.vector(Vector3)
    track = Vec()

    laserentry = Vector3(laser_entry[0], laser_entry[1], laser_entry[2])
    laserexit = Vector3(laser_exit[0], laser_exit[1], laser_exit[2])

    f = root_open("test.root", "recreate")
    track_tree = Tree('tracks')
    laser_tree = Tree('lasers')
    track_tree.create_branches({'track': stl.vector(Vector3)})
    laser_tree.create_branches({'entry': Vector3,
                                'exit': Vector3})

    for k in range(10):
        print(k)
        for i in range(1000):
            track.push_back(Vector3(i, k, k * i))

        track_tree.track = track
        track.clear()

        laser_tree.entry = Vector3(0, 0, 0)
        laser_tree.exit = Vector3(k, k, k)

        track_tree.fill()
        laser_tree.fill()

    track_tree.write()
    laser_tree.write()

    f.close()


def get_histos(filename, error=False):
    """ Read root file containing output of LaserFieldCalib  """
    dist_map = namedtuple("dist_map", "x y z")
    if error is False:
        axes = ['X', 'Y', 'Z']
    else:
        axes = ['X_Error', 'Y_Error', 'Z_Error']
    maps = []
    for ax in axes:
        rfile = ROOT.TFile(filename)
        print(ax)
        hist = rfile.Get('Reco_Displacement_' + ax)
        histo = rn.hist2array(hist)
        maps.append(histo)
    return dist_map(*maps)


def make_array(histos):
    """ Convert the histos from FieldCalib input to a nice numpy array """
    histo_shape = histos.x.shape
    distortion = np.zeros(histo_shape, dtype=[('dx', np.float), ('dy', np.float), ('dz', np.float)])
    distortion[:, :, :]['dx'] = histos.x
    distortion[:, :, :]['dy'] = histos.y
    distortion[:, :, :]['dz'] = histos.z

    return distortion


def filter_max(distortion, threshold=100000.):
    """ Resetting field distortion map values above certain value to 0 """
    for dir in ['dx', 'dy', 'dz']:
        idx = np.where(distortion[dir] > threshold)
        for x,y,z in zip(idx[0], idx[1], idx[2]):
            distortion[x,y,z][dir] = 0
    return distortion.view(np.recarray)


def find_unique_polar(angles, digits=2):
    """ Finds unique entries in an array of angles """
    return np.unique(np.round(angles, decimals=digits))


def find_unique_polar_idx(laser_data, precision=0.01):
    """ Returns all indices associate with a certain angle of the recorded laser track
    (can vary on the precision used) """
    angles = [laser[8] for laser in laser_data]
    horizontal_scans_slices = []
    for polar in find_unique_polar(angles):
        horizontal_scans_slices.append(np.where((angles < polar + precision) & (angles > polar - precision)))

    return horizontal_scans_slices


def setup_logging(run_number):
    # set up logging to file - see previous section for more details
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-4s %(levelname)-4s %(message)s',
                        datefmt='%H:%M:%S',
                        filename='./log/selecter-{}-{}.log'.format(run_number,
                                                                   time.strftime("%Y-%m-%d-%H-%M", time.gmtime())),
                        filemode='w')

    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(asctime)s %(name)-4s: %(levelname)-4s %(message)s',
                                  datefmt='%H:%M:%S',)
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)

    # Now, we can log to the root logger, or any other logger. First the root...
    logging.info('Logger started')

    return logging