import larana.lar_data as lard
import numpy as np



def time_to_distance(ticks, offset=3200, sampling=500, field=75):
    drift_speed = 0.75 * 10000 # cm / nsec
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
    ''' Chooses the closest entry in the supplied array to value.
    If two values are identical, return the first entry.'''
    idx = (np.abs(array-value)).argmin()
    return idx, array[idx]

def check_multiplicity(array):
    ''' checks how many entries in the input array are identical
    to the first entry starting at the first entry.  '''
    idx = 0
    while array[idx] == array[idx+1]:
        idx = idx + 1

    if idx == 0:
        return False, idx
    else:
        return True, idx