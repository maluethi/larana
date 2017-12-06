from larana.lar_utils import find_tree, get_branches, disassemble_laser, disassemble_track
import root_numpy as rn
import numpy as np


class LarData:
    """ Class to read exctracted files """
    def __init__(self, filename):
        self.filename = filename

        self._laser = []
        self._tracks = []
        self._truth = []

        self.read_laser()
        self.read_tracks()
        self.read_tracks(source='sim')

    def read_laser(self):
        try:
            laser_raw = self.read_trees("Laser", leafs=['dir', 'pos'])
            for lasr in laser_raw:
                self._laser.append(Laser(lasr))
        except EOFError as e:
            print(e)
            
    def read_tracks(self, source="data"):
        if source == "data":
            tree = "Tracks"
        elif source == "sim":
            tree = 'True'
        else:
            raise ValueError("unknown source: {}".format(source))
        try:
            track_raw = self.read_trees(tree)
        except EOFError as e:
            print(e)
            return
        except ValueError as e:
            print(e)
            return

        for track in track_raw:
            if source is 'data':
                self._tracks.append(Track(track))
            elif source is 'sim':
                self._truth.append(Track(track))

    def read_trees(self, treename, leafs=None):
        tree = find_tree(treename, self.filename)
        if leafs is not None:
            branches = get_branches(self.filename, tree, vectors=leafs)
        else:
            branches = get_branches(self.filename, tree)

        try:
            data = rn.root2array(self.filename, treename=tree, branches=branches)
        except:
            raise EOFError("tree '{}' data not present".format(treename))

        return data

    def laser(self, event):
        try:
            return self._laser[event]
        except IndexError:
            return []
        
    def track(self, event):
        try:
            track_in_event = [track for track in self._tracks if track.id == event]
        except IndexError:
            track_in_event = []
        return track_in_event
    
    def mctrack(self, event):
        try:
            mctrack_in_event = [track for track in self._truth if track.id == event]
        except IndexError:
            mctrack_in_event = []
        return mctrack_in_event
    
    def __getitem__(self, item):
        laser = self.laser(item)
        track = self.track(item)
        mctrack = self.mctrack(item)

        for tr in [laser, track, mctrack]:
            if tr is None:
                tr = []
        return laser, track, mctrack


class Laser():
    def __init__(self, raw_laser):
        las = disassemble_laser(raw_laser)
        self.id = las[4]
        self.entry = las[0].tolist()
        self.exit = las[1].tolist()
        self.dir = las[2].tolist()
        self.pos = las[3].tolist()


class Track():
    def __init__(self, raw_track):
        self.track, self.id = disassemble_track(raw_track)

    def __le__(self, other):
        return len(self.track.x)

    @property
    def x(self):
        return self.track.x

    @property
    def y(self):
        return self.track.y

    @property
    def z(self):
        return self.track.z