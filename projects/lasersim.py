from larana.laser_sim import *
from larana.geom import Laser
from pprint import pprint
from root_numpy import array2root

run_number = 11

laser_id = 2
azimu_start = 5
azimu_end = 11
azimu_steps = 1
polar_start = 150
polar_end = 210
polar_steps = 3

# sim laser location (for symmetric generation)
sim_laser_pos = [120., 150., 1036.35/2]

# generation
laser_scan = generate_span(laser_id, azimu_start, azimu_end, azimu_steps, polar_start, polar_end, polar_steps)
#pprint(laser_scan)
uboone_directions = [convert_to_uboone(azi, pol, r, laser_id) for azi, pol, r in laser_scan]
entry_points = [get_tpc_intersection(sim_laser_pos, direct)[0] for direct in uboone_directions]

pprint(entry_points)
# laser
la = Laser(laser_id)
raw_directions = [[la.polar_laser2tick(pol), la.azimu_laser2raw(azi)] for azi, pol, _ in laser_scan]
#pprint(raw_directions)

# time map
map = np.arange(0, len(laser_scan))
arr = np.array(map, dtype=[("map", np.uint32)])

# writing to file
outdir = '/home/matthias/workspace/larana/projects/out/lcs2/'
gen_textfile(outdir + 'input-{:d}.txt'.format(run_number), entry_points, uboone_directions)
gen_laserfile(outdir + 'Run-{:d}.txt'.format(run_number), raw_directions, laser_id=laser_id)
array2root(arr, outdir + 'TimeMap-{:d}.root'.format(run_number), mode='recreate')


from larana.lar_utils import make_figure, plot_edges
import matplotlib.pyplot as plt
fig, ax = make_figure()

inters = [get_tpc_intersection(sim_laser_pos, direct) for direct in uboone_directions]

for intrsec in inters:
    plot_edges(ax, intrsec[0], intrsec[1])

plt.show()