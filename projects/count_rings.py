from larana import lar_utils as lu

import numpy as np
from scipy import signal
import matplotlib.pyplot as plt


from matplotlib.collections import PatchCollection, LineCollection
from matplotlib.patches import Rectangle

in_file = "/home/matthias/laser/v06_26_02/scratch/RwaData-3166-12016.root"

raw = lu.read_raw(in_file).view(np.recarray)



print(raw[1][0])
fig, ax = plt.subplots()
hits = []
peaks = []
max_idx = []
max_peak = []

start_p = 5600

for wire in raw:
    baseline = np.mean(wire[4])
    raw_digits = wire[4][start_p:start_p+3200] - baseline
    #base= baseline(raw_digits,100)

    peak_idx = signal.find_peaks_cwt(raw_digits, np.arange(10,70),min_snr=2)

    peak = ([raw_digits[idx] for idx in peak_idx])
    hits.append(peak_idx)
    peaks.append(peak)

    print(peak_idx)
    idx = np.argmax(peak)

    max_idx.append(peak_idx[idx] + start_p)
    max_peak.append(peak[idx])

ax.plot(max_idx, max_peak, "x", markersize=10)
ax.set_ylim([-25, 100])


stepsize = 73
first_ring = 3200


rings = np.arange(first_ring - 1. * stepsize, 8000, stepsize)
for i, ring in enumerate(rings):

    ring = ring
    plt.text(ring, 100, str(i))
    rect = Rectangle([ring-10, 0], 20, 400.0, facecolor='red', alpha=0.5)
    ax.add_patch(rect)

for wire in raw:
    baseline = np.mean(wire[4])
    raw_digits = wire[4] - baseline
    ax.plot(raw_digits)

laser_pos = 5066
rect = Rectangle([laser_pos-10, 0], 20, 400.0, facecolor='green', alpha=0.9)
ax.add_patch(rect)

plt.title("Event 12015")

plt.xlabel("ticks")
plt.ylabel("ADC")

plt.xlim([0, 8500])
plt.ylim([-100, 400])

plt.show()


plt.hist(np.diff(max_idx),bins=50,range=[-100,0])
plt.xlabel("peak distance [ticks]")
plt.ylabel("N")
plt.show()

