from larana import lar_utils as laru
import numpy as np

import glob

import multiprocessing as mp


def get_histo(in_file):
    print("Processing:", in_file)
    raw = laru.read_raw(in_file)

    event_ids = np.unique([wire[0] for wire in raw])
    #wire_ids = np.unique([wire[2] for wire in raw])

    maxima = np.zeros([3456, len(event_ids)])

    for wire in raw:
        wire_id = wire[2]
        event = wire[0]

        baseline = np.mean(wire[4])
        raw_digits = wire[4] - baseline
        maxima[wire_id, event-1 - event_ids[0]] = np.argmax(raw_digits)

    return maxima

file_path = '/home/data/uboone/laser/7275/'
in_files = glob.glob(file_path + 'Rw*')
print(in_files)

pool = mp.Pool(processes=2)
res = pool.map(get_histo, in_files)
np.save('out/time-histo/histo-1.npy', res)
print("saved file to: 'out/time-histo/histo-1.npy'")