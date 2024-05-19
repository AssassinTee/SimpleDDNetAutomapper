class TileStatus:
    """
    This class holds all properties of a tile, which describe how a tile IS modified
    E.G the tile is flipped, rotated or set to empty
    """
    def __init__(self):
        self.v_flip = False
        self.h_flip = False
        self.rot = 0
        self.empty = False

    def __copy__(self) -> "TileStatus":
        t = TileStatus()
        t.v_flip = self.v_flip
        t.h_flip = self.h_flip
        t.rot = self.rot
        t.empty = self.empty
        return t

    def vFlip(self):
        status = self.__copy__()
        status.v_flip = not self.v_flip
        return status

    def hFlip(self):
        status = self.__copy__()
        status.h_flip = not self.h_flip
        return status

    def rot45(self):
        status = self.__copy__()
        status.rot += 45
        status.rot %= 360
        return status

    def rot90(self):
        status = self.__copy__()
        status.rot += 90
        status.rot %= 360
        return status

    def __eq__(self, other):
        if isinstance(other, TileStatus):
            return self.v_flip == other.v_flip and \
                self.h_flip == other.h_flip and \
                self.rot == other.rot and \
                self.empty == other.empty
        raise NotImplementedError
