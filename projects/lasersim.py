from larana.laser_sim import *
from larana.geom import Laser
from pprint import pprint
from root_numpy import array2root

run_number = 3

laser_id = 2
azimu_start = 35
azimu_end = -5
azimu_steps = 100
polar_start = 70
polar_end = 110
polar_steps = 10

# sim laser location (for symmetric generation)
sim_laser_pos = [120., 0., 1075.]

# generation
laser_scan = generate_span(laser_id, azimu_start, azimu_end, azimu_steps, polar_start, polar_end, polar_steps)
pprint(laser_scan)
uboone_directions = [convert_to_uboone(azi, pol, r, laser_id) for azi, pol, r in laser_scan]
entry_points = [get_tpc_intersection(sim_laser_pos, direct)[0] for direct in uboone_directions]
pprint(entry_points)
# laser
la = Laser(laser_id)
raw_directions = [[la.polar_laser2tick(pol), la.azimu_laser2raw(azi)] for azi, pol, _ in laser_scan]
pprint(raw_directions)

# time map
map = np.arange(0, len(laser_scan))
arr = np.array(map, dtype=[("map", np.uint32)])

# writing to file
outdir = '/home/matthias/workspace/larana/projects/out/'
gen_textfile(outdir + 'input.txt', entry_points, uboone_directions)
gen_laserfile(outdir + 'Run-{:d}.txt'.format(run_number), raw_directions, laser_id=laser_id)
array2root(arr, outdir + 'TimeMap-{:d}.root'.format(run_number), mode='recreate')

