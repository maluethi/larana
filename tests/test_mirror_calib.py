from larana.lar_utils import close_to_side
from numpy.testing import assert_array_almost_equal
import numpy as np

class TestIntersection(object):
    def test_close2side_laser1(self):


        x = np.linspace(1., 1035., 100.)
        y = x
        z = x
        track = np.rec.array([x, y, z],
                         dtype=[('x', 'f'), ('y', 'f'), ('z', 'f')])

        laserid = 1
        assert(close_to_side(track, 10, laserid))
        assert(not close_to_side(track, 0.1, laserid))

        laserid = 2
        assert(close_to_side(track, 10, laserid))
        assert(not close_to_side(track, 0.1, laserid))