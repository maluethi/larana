from larana.kal_utils import check_multiplicity, choose_nearest

import numpy as np

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

