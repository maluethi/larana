from larana import lar_utils as laru
import numpy as np
import glob
import multiprocessing as mp
from lmfit import Model, Parameters
from lmfit.models import GaussianModel
import os
import argparse
from functools import partial

def gaussian(x, amp, cen, wid):
    "1-d gaussian: gaussian(x, amp, cen, wid)"
    return (amp/(np.sqrt(2*np.pi)*wid)) * np.exp(-(x-cen)**2 /(2*wid**2))

def get_gauss_fit(x, y, center_guess):
    gmodel = Model(gaussian)
    params = Parameters()
    params.add('amp', value=50, min=5, max=np.inf)
    params.add('cen', value=center_guess, min=-250, max=250)
    params.add('wid', value=50)

    mod = GaussianModel()
    pars = mod.guess(y, x=x)
    out = mod.fit(y, pars, x=x)

    return out


def get_histo(in_file, only_max=False):
    mid = mp.current_process()._identity[0]
    print("[{}] Processing: {}".format(mid, in_file))
    raw = laru.read_raw(in_file)

    event_ids = np.unique([wire[0] for wire in raw])
    #wire_ids = np.unique([wire[2] for wire in raw])
    previous_event = event_ids[0]
    maxima = np.zeros([3456, len(event_ids)])
    std_maxima = np.zeros([3456, len(event_ids)])
    ticks = np.arange(0, len(raw[0][4]))

    for wire in raw:
        wire_id = wire[2]
        event = wire[0]

        baseline = np.mean(wire[4])
        raw_digits = wire[4] - baseline

        if only_max:
            maxima[wire_id, event-1 - event_ids[0]] = np.argmax(raw_digits[900:1200])

        else:
            try:
                res = get_gauss_fit(ticks, raw_digits, np.argmax(raw_digits))
                amp = res.params['amplitude']
                cen = res.params['center']
                wid = res.params['sigma']
            except:
                wid = -9999.
                cen = -9999.

            idx = event - 1 - event_ids[0]
            maxima[wire_id, idx] = cen
            std_maxima[wire_id, idx] = wid

        if (previous_event != event):
            print("[{}] Processing: {}/{}".format(mid, event, event_ids[-1]))

        previous_event = event

    return [maxima, std_maxima, event_ids[0]]


parser = argparse.ArgumentParser(description='Little script to compute maximas in files')
parser.add_argument('base_dir',  action="store", type=str, help='base directory')
parser.add_argument('-n', action="store", type=int, default=1, help='number of processes')
parser.add_argument('-s', action='store_true', default=False, dest='single', help='process single file')
parser.add_argument('-m', action='store_true', default=False, dest='max', help='only calculate maxima, no gauss fits')

args = parser.parse_args()
file_path = args.base_dir

if not os.path.isdir(file_path):
    raise FileNotFoundError("Path: {} not found".format(file_path))

in_files = glob.glob(file_path + 'Rw*[0-3][0-9]*')
if args.single:
    in_files = [in_files[0]]

print(in_files)
pool = mp.Pool(processes=args.n)

partial_hist = partial(get_histo, only_max=args.max)

res = pool.map(partial_hist, in_files)

np.save('out/time-histo/histo-more-maxima.npy', res)
print("saved file to: 'out/time-histo/histo-more-maxima.npy'")