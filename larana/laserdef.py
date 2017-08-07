from . base import Base


class Laseref(Base):

    def __init__(self, branch=None):
        super(Laseref, self).__init__()
        self.data_product = "Laser Data"
        self.tree = "Events"

        if branch is None:
            self.producer = "LaserHitAna"
            # self.branch = "lasercal::LaserBeam_LaserMerger_LaserBeam_" + self.producer + ".obj."

            self.branch = "lasercal::LaserBeam_LaserDataMerger_LaserBeam_" + self.producer + ".obj."
        else:
            self.branch = branch[0] + ".obj."

        self.XYZ = ["X", "Y", "Z"]

    def pos(self):
        return self.gen_string("fLaserPosition.f", self.XYZ)

    def dir(self):
        return self.gen_string("fDirection.f", self.XYZ)

    def entry_point(self):
        return self.gen_string("fEntryPoint.f", self.XYZ)

    def exit_point(self):
        return self.gen_string("fExitPoint.f", self.XYZ)

    def power(self):
        return self.gen_string("fPower")

    def id(self):
        return self.gen_string("fLaserID")
