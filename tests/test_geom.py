import larana.geom as gm
from numpy.testing import assert_array_almost_equal, assert_almost_equal
from larana.lar_utils import TPC
import numpy as np

class TestIntersection(object):
    def test_simple(self):
        box = [0, 1, 0, 1, 0, 1]
        point = [-0.5, 0.5, 0.5]
        direction = [1, 0, 0]

        pt_entry, pt_exit = gm.get_tpc_intersection(point, direction, box=box)
        assert_array_almost_equal(pt_entry, [0., 0.5, 0.5])
        assert_array_almost_equal(pt_exit, [1, 0.5, 0.5])

    def test_tpc(self):
        point = [120, 0, -10]
        direction = [0, 0, 1]

        pt_entry, pt_exit = gm.get_tpc_intersection(point, direction)
        assert_array_almost_equal(pt_entry, [120., 0., TPC.z_min])
        assert_array_almost_equal(pt_exit, [120, 0, TPC.z_max])

    def test_dist(self):
        a = [0,0,0]
        b = [1,0,0]

        d = gm.distance(a, b)
        assert_almost_equal(d, 1.0)

        a = [0,0,1]
        b = [1,0,0]

        d = gm.distance(a, b)
        assert_almost_equal(d, np.sqrt(2.0))

        a = [0,0,1]
        b = np.array([1,0,0])

        d = gm.distance(a, b)
        assert_almost_equal(d, np.sqrt(2.0))

class TestLaser:
    def test_azimu2raw(self):
        la = gm.Laser(laser_id=2)

        # the actual calibration
        deg1 = la.azimu_laser2raw(6.4924139)
        assert_almost_equal(deg1, 155.466003480)

        # some other point
        deg2 = la.azimu_laser2raw(0)
        assert_almost_equal(deg2, 161.95841738)

    def test_polar2raw(self):
        la = gm.Laser(laser_id=2)

        # the calibration
        raw = la.polar_laser2raw(0.3868181)
        assert_almost_equal(raw, 297.308059, decimal=5)

        # other point
        raw = la.polar_laser2raw(0)
        assert_almost_equal(raw, 296.921182, decimal=3)

class TestPoint:
    def test_point_distance(self):
        pt1 = gm.Point(1,1)
        pt2 = gm.Point(1,1)

        d = pt1.dist(pt2)
        assert_almost_equal(d, 0.)

        pt2 = gm.Point(2, 2)
        d = pt1.dist(pt2)
        assert_almost_equal(d, np.sqrt(2))

        d = pt2.dist(pt1)
        assert_almost_equal(d, np.sqrt(2))

    def test_point_angle(self):
        pt1 = gm.Point(1, 1)
        pt2 = gm.Point(2, 2)

        a = pt1.angle(pt2)
        assert_almost_equal(np.rad2deg(a), 45.)

class TestRing:
    def test_tangent(self):
        center = gm.Point(1,1)
        circ = gm.Ring(center, 1)

        pt = gm.Point(0,0)

        tang = circ.tangent(pt)

        assert_almost_equal(tang[0], 0.)
        assert_almost_equal(np.rad2deg(tang[1]), 90.)

class TestLine:
    def test_line(self):
        pt = gm.Point(0,0)
        m = 45 #deg

        line = gm.Line(pt, m)
        y = line.at(1)
        assert_almost_equal(y, 1.0)


