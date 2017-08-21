from larana.laser_sim import *

laser_id = 2
azimu_start = -1
azimu_end = 1
azimu_steps = 3
polar_start = 89
polar_end = 91
polar_steps = 3

laser_scan = generate_span(laser_id, azimu_start, azimu_end, azimu_steps, polar_start, polar_end, polar_steps)
directions = [convert_to_uboone(azi, pol, r, laser_id) for azi, pol, r in laser_scan]
entry_points = [get_tpc_intersection(LASER_POS[laser_id], direct)[0] for direct in directions]
gen_textfile('/home/matthias/workspace/larana/projects/out/input.txt', entry_points, directions)