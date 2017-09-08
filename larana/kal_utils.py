import larana.lar_data as lard
from larana.lar_utils import WIRE
import numpy as np

slope = {"u": np.tan(np.deg2rad(30)),
         "v": np.tan(np.deg2rad(-30))}

wire_spacing = 0.3  # cm
ind_wire_spacing_btom = wire_spacing * 1 / np.sin(np.deg2rad(30))
ind_wire_spacing_side = wire_spacing * 1 / np.sin(np.deg2rad(60))

# construct the wire vectors
y_botm_wires = np.arange(WIRE.z_min, WIRE.z_max + 0.3, wire_spacing)  # seems there is more col wires

u_side_wires = np.arange(WIRE.y_min, WIRE.y_max, ind_wire_spacing_side)
u_btom_wires = np.arange(WIRE.z_min, WIRE.z_max, ind_wire_spacing_btom)

v_side_wires = u_side_wires
v_botm_wires = u_btom_wires

def time_to_distance(ticks, offset=3200, sampling=500, field=75):
    drift_speed = 0.75 * 10000  # cm / nsec
    return (ticks - offset) * sampling / drift_speed

def get_x(df, event, plane):
    ticks = lard.get_tick(df, event, plane)
    return time_to_distance(ticks)

def get_z(df, event, plane):
    wire = lard.get_wire(df, event, plane)
    return wire * 0.3

def get_x_width(df,event, plane):
    width = lard.get_width(df, event, plane)
    return time_to_distance(width, offset=0)

def choose_nearest(array, value):
    """ Chooses the closest entry in the supplied array to value.
    If two values are identical, return the first entry."""
    idx = (np.abs(array-value)).argmin()
    return idx, array[idx]

def check_multiplicity(array):
    """ checks how many entries in the input array are identical
    to the first entry starting at the first entry.  """
    idx = 0

    if len(array) == 1:
        return False, idx

    while array[idx] == array[idx+1]:
        idx += 1
        if idx + 1 == len(array):
            break

    if idx == 0:
        return False, idx
    else:
        return True, idx


def get_side_corssing(xyz, plane):
    x, y, z = xyz
    if plane is "u":
        # crossing side at z = 0
        y_cross = [slope[plane] * (WIRE.z_min - z) + y, WIRE.z_min]
    if plane is "v":
        # crossing side at z = upstream max (~1000cm)
        y_cross = [slope[plane] * (WIRE.z_max - z) + y, WIRE.z_max]
    return y_cross


def get_bottom_crossing(xyz, plane):
    x, y, z = xyz
    z_cross = (WIRE.y_min - y) / slope[plane] + z
    return [WIRE.y_min, z_cross]


def nearest_wire(point_ub, return_start=False, plane=None):
    x, y, z = point_ub

    # now find the bottom crossings
    u_botm_crossing = get_bottom_crossing(point_ub, "u")[1]
    v_botm_crossing = get_bottom_crossing(point_ub, "v")[1]

    if u_botm_crossing > WIRE.z_min:
        # just search for the wire closest to u along the z axis
        ind0_closest_idx = np.argmin(np.abs(u_btom_wires - u_botm_crossing))
        ind0_closest_start = [WIRE.y_min, u_btom_wires[ind0_closest_idx]]
        ind0_closest_idx += len(u_side_wires)
    if u_botm_crossing < WIRE.z_min:
        # calculate where u crosses the side
        u_side_crossing = get_side_corssing(point_ub, "u")[0]
        ind0_closest_idx = np.argmin(np.abs(u_side_wires - u_side_crossing))
        ind0_closest_start = [u_side_wires[ind0_closest_idx], WIRE.z_min]
        ind0_closest_idx = len(u_side_wires) - ind0_closest_idx

    if v_botm_crossing < WIRE.z_max:
        # just search for the wire closest to u along the z axis
        ind1_closest_idx = np.argmin(np.abs(v_botm_wires - v_botm_crossing))
        ind1_closest_start = [WIRE.y_min, v_botm_wires[ind1_closest_idx]]
    if v_botm_crossing > WIRE.z_max:
        v_side_crossing = get_side_corssing(point_ub, "v")[0]
        ind1_closest_idx = np.argmin(np.abs(v_side_wires - v_side_crossing))
        ind1_closest_start = [v_side_wires[ind1_closest_idx], WIRE.z_max]
        ind1_closest_idx += len(v_botm_wires)

    col_closest_idx = np.searchsorted(y_botm_wires, z)

    # handle corner cases
    if col_closest_idx >= len(y_botm_wires):
        if z - 0.6 < WIRE.z_max:
            col_closest_idx -= 1
        else:
            raise ValueError("point is outside wire reach (downstream)")
    if col_closest_idx == 0:
        if z + 0.6 < WIRE.z_min:
            col_closest_idx += 1
        else:
            pass
            #raise ValueError("point is outside wire reach (upstream)")

    col_closest_start = [WIRE.y_min, y_botm_wires[col_closest_idx]]

    if not return_start:
        return ind0_closest_idx, ind1_closest_idx, col_closest_idx
    else:
        return col_closest_idx, col_closest_start, \
               ind0_closest_idx, ind0_closest_start, \
               ind1_closest_idx, ind1_closest_start
