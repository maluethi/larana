import larana.geom as gm
from numpy.testing import assert_array_almost_equal
from larana.lar_utils import TPC

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