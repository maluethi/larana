from larana.laser_sim import *
from numpy.testing import assert_array_almost_equal

class TestIntersection(object):
    def test_carthesian(self):

        laser_id = 0
        azimu_start = 0
        azimu_end = 2
        azimu_steps = 2

        polar_start = 0
        polar_end = 2
        polar_steps = 2

        sim = generate_span(laser_id, azimu_start, azimu_end, azimu_steps, polar_start, polar_end, polar_steps)
        print(sim)
        assert_array_almost_equal(sim, [[0, 0, 1],
                                        [2, 0, 1],
                                        [0, 2, 1],
                                        [2, 2, 1]])
