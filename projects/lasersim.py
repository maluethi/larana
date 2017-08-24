from larana.laser_sim import *
from larana.geom import Laser
from pprint import pprint
from root_numpy import array2root

run_number = 1

laser_id = 2
azimu_start = 30
azimu_end = -5
azimu_steps = 35
polar_start = 60
polar_end = 120
polar_steps = 30

# generation
laser_scan = generate_span(laser_id, azimu_start, azimu_end, azimu_steps, polar_start, polar_end, polar_steps)
uboone_directions = [convert_to_uboone(azi, pol, r, laser_id) for azi, pol, r in laser_scan]
entry_points = [get_tpc_intersection(LASER_POS[laser_id], direct)[0] for direct in uboone_directions]

# laser
la = Laser(laser_id)
raw_directions = [[la.polar_laser2tick(pol), la.azimu_laser2raw(azi)] for azi, pol, _ in laser_scan]

# time map
map = np.arange(0, len(laser_scan))
arr = np.array(map, dtype=[("map", np.uint32)])
print(map)

# writing to file
outdir = '/home/matthias/workspace/larana/projects/out/'
gen_textfile(outdir + 'input.txt', entry_points, uboone_directions)
gen_laserfile(outdir + 'Run-{:04d}.txt'.format(run_number), raw_directions, laser_id=laser_id)
array2root(arr, outdir + 'TimeMap-{:04d}.root'.format(run_number), mode='recreate')