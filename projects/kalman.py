import larana.lar_data as lard
import larana.lar_utils as laru
import larana.kal_utils as lark

import matplotlib.pyplot as plt
import numpy as np

from filterpy.kalman import KalmanFilter
from filterpy.common import Q_discrete_white_noise


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

def get_kalman():
    kf = KalmanFilter(dim_x=2, dim_z=1)

    dz = 0.3

    kf.x = np.array([138.0, -0.1])

    kf.R = 2
    kf.F = np.array([[1., dz],
                     [0., 1.]])
    kf.H = np.array([[1., 0.]])
    kf.P *= [5., 2.]

    kf.Q = Q_discrete_white_noise(2, dz, 2.)

    return kf

def filter_kalman(kf, x_data, y_data, y_width):
    xs, ts, pr, ps = [], [], [], []

    first = True
    last_z = 0
    n_multip = 0

    for idx in range(len(track_z)):
        z, x, width = x_data[idx], y_data[idx], y_width[idx]
        dz = z - last_z

        if n_multip != 0:
            n_multip -= 1
            continue

        # if we have way too large gaps, just stop it
        if np.abs(dz) > 150. and not first:
            break

        kf.F[0, 1] = dz
        kf.R = width
        kf.Q = Q_discrete_white_noise(2, dz, .05)
        pred, _ = kf.get_prediction()
        delta = np.abs(pred[0] - x)

        if not first:
            # print("{} value at: {}, {}".format(idx, last_z, z))
            # if the prediction is too far off the expected, we assume this is an outlier
            if delta > np.abs(dz) * 0.5 / 0.3:
                continue

        # if we have multiple hits on the wire, choose the closest one to the prediction as the next measurement
        multip, n_multip = lark.check_multiplicity(track_z[idx:])
        if multip:
            # print("multi value: at {} {}  {}".format(z, n_multip, track_x[idx:idx + n_multip+1]))
            closest_idx, closest_val = lark.choose_nearest(track_x[idx:idx + n_multip + 1], pred[0])
            x = closest_val

        kf.predict()
        kf.update(x)

        xs.append(kf.x.T[0])
        ts.append(z)
        pr.append(pred[0])
        ps.append(kf.P.diagonal()[0])

        first = False
        last_z = z

    return xs, ts, pr, ps

subrun = 789

filename = "/home/data/uboone/laser/7267/out/roi/LaserReco-LaserHit-7267-0{}_digitfilter-exp-roi.root".format(subrun)
np.set_printoptions(precision=4)

df = lard.LarData(filename)
df.read_ids()
df.read_hits(planes="u")
df.read_laser()

for evt in range(50):

    fig, axes = plt.subplots(3,1)
    laser_data = df.get_laser(evt)

    laser_entry = [laser_data['entry_{}'.format(dim)] for dim in "xyz"]
    laser_exit = [laser_data['exit_{}'.format(dim)] for dim in "xyz"]
    laser_entry_wireidx = lark.nearest_wire(laser_entry)
    laser_exit_wireidx = lark.nearest_wire(laser_exit)

    event = evt
    for plane in reversed(range(3)):


        print(laser_entry_wireidx)
        print(laser_exit_wireidx)

        print(lard.get_wire(df, event, plane))

        track_z = get_z(df, event, plane)
        track_x = get_x(df, event, plane)
        width_x = get_x_width(df, event, plane)

        track_z = np.flipud(track_z)
        track_x = np.flipud(track_x)
        width_x = np.flipud(width_x)

        kf = get_kalman()
        xs, ts, pr, ps = filter_kalman(kf, track_z, track_x, width_x)


        plt.title("event {}".format(event))
        axes[plane].plot(track_z, track_x, "o", alpha=0.2)
        axes[plane].errorbar(ts, xs, yerr=np.array(ps))
        axes[plane].plot(ts, ps)
        axes[plane].plot(laser_entry_wireidx[plane] * 0.3, laser_entry[0], '*', markersize=10)
        axes[plane].plot(laser_exit_wireidx[plane] * 0.3, laser_exit[0], '*', markersize=10)

        axes[plane].plot(ts, pr, '.')
        axes[plane].plot([laser_entry[2], laser_exit[2]], [laser_entry[0], laser_exit[0]], 'r-')
    plt.show()

