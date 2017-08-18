from larana.kal_utils import check_multiplicity, choose_nearest, nearest_wire, get_side_corssing, get_bottom_crossing
from larana.lar_utils import WIRE

import numpy as np
from numpy.testing import assert_almost_equal

class TestMultiplicity(object):
    def test_false(self):
        a = np.array([0, 1, 2, 2, 4])
        flag, n = check_multiplicity(a)
        assert(flag == False)
        assert(n == 0)

    def test_true_one(self):
        a = np.array([0, 0, 2, 2])
        flag, n = check_multiplicity(a)
        assert(flag == True)
        assert(n == 1)

    def test_true_multiple(self):
        a = np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2])
        flag, n = check_multiplicity(a)
        assert(flag == True)
        assert(n == 8)

    def test_short(self):
        a = np.array([1])
        flag, n = check_multiplicity(a)
        assert(flag == False)
        assert(n == 0)

    def test_single_values(self):
        a = np.array([1,1,1,1])
        flag, n = check_multiplicity(a)
        assert(flag == True)
        assert(n == 3)


class TestChooseNearest(object):
    def test_simple(self):
        a = np.array([1., 2., 3.])
        val = 2.
        idx, val = choose_nearest(a, val)
        assert(idx == 1)
        assert(val == 2.)

    def test_single(self):
        a = np.array([1.])
        val = 2.
        idx, val = choose_nearest(a, val)
        assert(idx == 0)
        assert(val == 1.)

    def test_multiple(self):
        a = np.array([1., 1., 1.])
        val = 2.
        idx, val = choose_nearest(a, val)
        assert(idx == 0)
        assert(val == 1.)

    def test_negative_vals(self):
        a = np.array([-1., 2., 3.])
        val = 0.
        idx, val = choose_nearest(a, val)
        assert(idx == 0)
        assert(val == -1.)

class TestWireFinding(object):
    def test_side_crossing(self):
        pts_on_axis = [[0, 0, z] for z in range(1000)]
        for pt in pts_on_axis:
            cross_u = get_side_corssing(pt, "u")
            assumed_u = [- np.tan(np.deg2rad(30)) * (pt[2] - WIRE.z_min), WIRE.z_min]

            cross_v = get_side_corssing(pt, "v")
            assumed_v = [np.tan(np.deg2rad(-30)) * (WIRE.z_max - pt[2]), WIRE.z_max]

            assert_almost_equal(cross_u, assumed_u)
            assert_almost_equal(cross_v, assumed_v)

    def test_bottom_crossing(self):
        pts_on_axis = [[0, 0, z] for z in range(1, 1000)]
        for pt in pts_on_axis:
            cross_u = get_bottom_crossing(pt, "u")
            assumed_u = [WIRE.y_min, pt[2] + WIRE.y_min / np.tan(np.deg2rad(30))]
            assert_almost_equal(cross_u, assumed_u)

            cross_v = get_bottom_crossing(pt, "v")
            assumed_v = [WIRE.y_min, pt[2] + WIRE.y_min / np.tan(np.deg2rad(-30))]
            assert_almost_equal(cross_v, assumed_v)

    def test_nearest_z0_y0(self):
        """
            |-----------------------------------------------------|
            |                                                     |
            |                                                     |
          y | o                                                   |
            |/ \                                                  |
            |   \                                                 |
            |----\------------------------------------------------|
                                        z
        """
        xyz = [0., 2., 0.1]
        col_idx, col_start, u_idx, u_start, v_idx, v_start = nearest_wire(xyz, return_start=True)

        u_crossing_side = get_side_corssing(xyz, "u")
        v_crossing_botm = get_bottom_crossing(xyz, "v")

        assert(np.allclose(u_start, u_crossing_side, atol=0.6))
        assert(np.allclose(v_start, v_crossing_botm, atol=0.6))

    def test_nearest_z500_y0(self):
        """
            |-----------------------------------------------------|
            |                                                     |
            |                                                     |
          y |                          o                          |
            |                         / \                         |
            |                        /   \                        |
            |-----------------------/-----\-----------------------|
                                        z
        """
        xyz = [0., 0., 500.]
        col_idx, col_start, u_idx, u_start, v_idx, v_start = nearest_wire(xyz, return_start=True)

        u_crossing_botm = get_bottom_crossing(xyz, "u")
        v_crossing_botm = get_bottom_crossing(xyz, "v")

        assert(np.allclose(u_start, u_crossing_botm, atol=0.6))
        assert(np.allclose(v_start, v_crossing_botm, atol=0.6))

    def test_nearest_z1000_y0(self):
        """
            |-----------------------------------------------------|
            |                                                     |
            |                                                     |
          y |                                                   o |
            |                                                  / \|
            |                                                 /   |
            |------------------------------------------------/----|
                                        z
        """
        xyz = [0., 0., 1033.]
        col_idx, col_start, u_idx, u_start, v_idx, v_start = nearest_wire(xyz, return_start=True)

        u_crossing_botm = get_bottom_crossing(xyz, "u")
        v_crossing_side = get_side_corssing(xyz, "v")

        assert(np.allclose(u_start, u_crossing_botm, atol=0.6))
        assert(np.allclose(v_start, v_crossing_side, atol=0.6))

    def test_nearest_z500_y100(self):
        """
            |-----------------------------------------------------|
            |                          o                          |
            |                         / \                         |
          y |                        /   \                        |
            |                       /     \                       |
            |                      /       \                      |
            |---------------------/---------\---------------------|
                                        z
        """
        xyz = [0., 100., 500.]
        col_idx, col_start, u_idx, u_start, v_idx, v_start = nearest_wire(xyz, return_start=True)

        u_crossing_botm = get_bottom_crossing(xyz, "u")
        v_crossing_botm = get_bottom_crossing(xyz, "v")

        assert(np.allclose(u_start, u_crossing_botm, atol=0.6))
        assert(np.allclose(v_start, v_crossing_botm, atol=0.6))