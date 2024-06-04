class TileStatus:
    """
    This class holds all properties of a tile, which describe how a tile IS modified
    E.G the tile is flipped, rotated or set to empty
    """
    def __init__(self):
        self.v_flip = False
        self.h_flip = False
        self.rot = False
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

    def rotate(self):
        """
        rotate 90 degrees
        NOTE: rotated can only be on or off, rotated by 180 degree means NOT rotated, hflipped and vflipped,
        while rotated by 270 degree means hflipped, vflipped and rotated
        """
        status = self.__copy__()
        if self.rot:
            status.rot = False
            status.v_flip = not self.v_flip
            status.h_flip = not self.h_flip
        else:
            status.rot = True
        return status

    def __eq__(self, other):
        if isinstance(other, TileStatus):
            return self.v_flip == other.v_flip and \
                self.h_flip == other.h_flip and \
                self.rot == other.rot and \
                self.empty == other.empty
        raise NotImplementedError
