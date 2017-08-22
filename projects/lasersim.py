from larana.laser_sim import *
from pprint import pprint
laser_id = 2
azimu_start = 30
azimu_end = -5
azimu_steps = 35
polar_start = 60
polar_end = 120
polar_steps = 30

laser_scan = generate_span(laser_id, azimu_start, azimu_end, azimu_steps, polar_start, polar_end, polar_steps)
uboone_directions = [convert_to_uboone(azi, pol, r, laser_id) for azi, pol, r in laser_scan]
#laser_directions =
entry_points = [get_tpc_intersection(LASER_POS[laser_id], direct)[0] for direct in uboone_directions]
pprint([get_tpc_intersection(LASER_POS[laser_id], direct)[1] for direct in uboone_directions])

gen_textfile('/home/matthias/workspace/larana/projects/out/input.txt', entry_points, uboone_directions)