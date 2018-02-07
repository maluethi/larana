
import larana.lar_utils as laru
import larana.geom as geo
import numpy as np

import matplotlib.pyplot as plt

logi = laru.setup_logging(123)

log = logi.getLogger('Selecter')

log.info("Well well")

CUTS = {"entry_region": 5.,
        "slope": 0.4,  # difference from expected to measured slope that is acceptable
        "smoothness": 1.}  # maximum stepsize in cm for a single step (acts on kinks)

in_file = "/home/data/uboone/laser/7267/tracks/Tracks-7267-roi.root"
#in_file = "/home/data/uboone/laser/sim/Tracks-lcs1-023_true.root"

tracks = laru.read_tracks(in_file) #, identifier="True")
lasers = laru.read_laser(in_file)

laser_id = 2

laser_pos = geo.LASER_POS[laser_id]

# generate event id lists, since there are more tracks than events
track_event_id = np.array([track[0] for track in tracks])
pol_incs = laru.find_unique_polar_idx(lasers)


good_tracks = []
good_lasers = []

# process tracks in bunches of constant polar angles
for pol_idx in pol_incs:
    good = []
    log.info("------- Procesing --------")
    for laser_idx, laser in enumerate(lasers[pol_idx]):
        laser_entry, laser_exit, dir, pos, evt = laru.disassemble_laser(laser)

        # calculate slope
        d = [ex - en for ex, en in zip(laser_exit.tolist(), laser_entry.tolist())]

        log.info("Event {}".format(evt))
        track_list = np.where(track_event_id == evt)
        # loop over all tracks in this event
        for track_idx, track in enumerate(tracks[track_list]):
            track_points, evt = laru.disassemble_track(track)
            track_id = track[0]

            # -------- Cuts should go in here and escape the loop -------- #
            # CUT 1: Entry region cut
            max_idx = np.argmax(track_points.z)
            if geo.distance(track_points[max_idx], laser_entry.tolist()) > CUTS["entry_region"]:
                log.info("event: {}, track {}: Outside entry region".format(evt, track_id))
                continue

            # CUT 2: Simple cut on the zy-slop to be in a reasonable range compared to the expected
            m, b = np.polyfit(track_points.z, track_points.y, 1)
            m_zy = d[1]/d[2]

            if np.abs((m_zy - m)/m_zy) > CUTS["slope"]:
                log.info("event: {}, track {}: Slope is not within expectations".format(evt, track_id))
                continue

            # CUT 3: Smoothness
            dy = np.abs(np.diff(track_points.y))
            if np.max(dy) > CUTS["smoothness"]:
                continue

            plt.plot(track_points.z[1:], dy)

            good.append([track_list[0][track_idx], pol_idx[0][laser_idx]])
    plt.show()

    good_tracks.append([item[0] for item in good])
    good_lasers.append([item[1] for item in good])

    # plotting per slice
    fig, ax = laru.make_figure()
    for track_idx, laser_id in zip(good_tracks[-1], good_lasers[-1]):

        track_id = tracks[track_idx][0]
        laser_id = lasers[laser_id][0]

        track_points, evt = laru.disassemble_track(tracks[track_idx])
        laru.plot_track(track_points.x, track_points.y, track_points.z, ax)

    plt.show()


# plotting & checks
for tr_sl, la_sl in zip(good_tracks, good_lasers):
    fig, ax = laru.make_figure()
    for track_idx, laser_id in zip(tr_sl, la_sl):

        track_id = tracks[track_idx][0]
        laser_id = lasers[laser_id][0]

        if track_id != laser_id:
            raise ValueError("Track Event ID and Laser Event ID mismatch: "
                             "laser_id {} / track_id {}".format(laser_id, track_id)
                             )
        track_points, evt = laru.disassemble_track(tracks[track_idx])
        laru.plot_track(track_points.x, track_points.y, track_points.z, ax)
    plt.show()
print(good_tracks)