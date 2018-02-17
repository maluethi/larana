from larana import lar_utils as lu

import numpy as np
from scipy import signal
import matplotlib.pyplot as plt


from matplotlib.collections import PatchCollection, LineCollection
from matplotlib.patches import Rectangle

in_file = "/home/matthias/laser/v06_26_02/scratch/RwaData-3166-240.root"

raw = lu.read_raw(in_file).view(np.recarray)



print(raw[1][0])
fig, ax = plt.subplots()
plt.title("Event 12014")
laser_pos = 5066
plt.text(laser_pos, 100, "Laser Entry")


for wire in raw:
    baseline = np.mean(wire[4])
    raw_digits = wire[4] - baseline
    ax.plot(raw_digits, alpha=0.5)


rect = Rectangle([laser_pos-10, -100], 20, 1000.0, facecolor='green', alpha=1)
ax.add_patch(rect)

plt.xlim([4500, 8500])
plt.ylim([-100, 400])
plt.xlabel("ticks")
plt.ylabel("ADC")
plt.show()

