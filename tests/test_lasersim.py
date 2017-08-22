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


class TestFiles:
    def test_laserfile(self, tmpdir):
        p = tmpdir.join("test.txt")
        azimu = [0, 1, 2, 3, 4]
        polar = [0, 1, 2, 3, 4]
        laser_id = 1
        gen_laserfile(str(p), azimu, polar, laser_id)

        with open(str(p)) as testfile:
            for idx, line in enumerate(testfile.readlines()):
                assert(int(line[0]) == laser_id)
                assert(int(line[6]) == idx)