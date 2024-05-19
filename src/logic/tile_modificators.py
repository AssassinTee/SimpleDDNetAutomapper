class TileMods:
    """
    This class holds all properties, that describe how a tile can be modified
    """
    def __init__(self, can_flip_h: bool, can_flip_v: bool, can_rot: bool):
        self.can_h_flip = can_flip_h
        self.can_v_flip = can_flip_v
        self.can_rot = can_rot

    def __eq__(self, other):
        if isinstance(other, TileMods):
            return self.can_h_flip == other.can_h_flip and \
                self.can_v_flip == other.can_v_flip and \
                self.can_rot == other.can_rot
        raise NotImplementedError

    def __copy__(self):
        return TileMods(self.can_h_flip, self.can_v_flip, self.can_rot)
