from larana.lar_tree import LarData
from numpy.testing import assert_array_almost_equal

class TestDataReading():
    def test_read_laser(self):
        lard = LarData("test_data.root")
        assert(len(lard.laser) == 5)