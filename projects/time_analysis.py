from larana import lar_utils as laru
import numpy as np
import glob
import multiprocessing as mp
from lmfit import Model, Parameters
from lmfit.models import GaussianModel
import sys

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


def get_histo(in_file):
    print("Processing:", in_file)
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
        #maxima[wire_id, event-1 - event_ids[0]] = np.argmax(raw_digits)

        res = get_gauss_fit(ticks, raw_digits, np.argmax(raw_digits))
        amp = res.params['amplitude']
        cen = res.params['center']
        wid = res.params['sigma']

        maxima[wire_id, event - 1 - event_ids[0]] = cen
        std_maxima[wire_id, event - 1 - event_ids[0]] = wid

        if (previous_event != event):
            print("Processing: {}/{}".format(event, event_ids[-1]))

        previous_event = event


    return [maxima, std_maxima]


base_dir = sys.argv[1]
if base_dir is None:
    file_path = '/home/data/uboone/laser/7275/rwa/'
else:
    file_path = base_dir

in_files = glob.glob(file_path + 'Rw*[0-3][0-9]*')

#in_files = '/home/data/uboone/laser/7275/rwa/RwaData-7275-006.root'
print(in_files)

pool = mp.Pool(processes=1)
res = pool.map(get_histo, in_files)

#res = get_histo(in_files)
print(res)
np.save('out/time-histo/histo-more-gauss.npy', res)
print("saved file to: 'out/time-histo/histo-more-gauss.npy'")