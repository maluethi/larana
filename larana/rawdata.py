from . base import Base

# Meh, this is super slow! So better don't use it...
class RawData(Base):
    def __init__(self):
        """ plane: Either U,V,Y for the different views """
        super(RawData, self).__init__()

        self.tree = "Events"

        self.product = ""
        self.branch = "raw::RawDigits_daq__Swizzler.obj"

    def ADC(self):
        return [self.gen_string(".fADC")]

    def Channel(self):
        return [self.gen_string(".fChannel")]