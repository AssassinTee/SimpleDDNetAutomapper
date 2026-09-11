from src.globals import EIGHT_NEIGHBORS, NUM_NEIGHBOR_BITS, NUM_NEIGHBOR_STATES, NEIGHBOR_BIT_COMPARATOR
from typing import List, Set

# relative (x, y) offsets of the 8-neighborhood, y positive means up (DDNet "Pos" convention)
NEIGHBOR_OFFSETS = [
    (-1, 1), (0, 1), (1, 1),
    (-1, 0), (1, 0),
    (-1, -1), (0, -1), (1, -1),
]
NEIGHBOR_INDEX_BY_OFFSET = {offset: index for index, offset in enumerate(NEIGHBOR_OFFSETS)}


class TileConnection:
    def __init__(self, neighbors: list):
        if len(neighbors) != EIGHT_NEIGHBORS:
            raise ValueError(f"Neighbors are not {EIGHT_NEIGHBORS}")
        for i in range(EIGHT_NEIGHBORS):
            if neighbors[i] < 0 or neighbors[i] >= 3:
                raise ValueError(f"neighbor[{i}] not in [0, 1]")
        self._neighbors = neighbors.copy()

    def encode(self) -> int:
        return self._encode(NUM_NEIGHBOR_BITS)

    def encodeSmall(self) -> int:
        # sanity check
        for i in range(EIGHT_NEIGHBORS):
            if self._neighbors[i] < 0 or self._neighbors[i] > 1:
                raise ValueError("Can't encode small, neighbors are only allowed in range [0, 1]")
        return self._encode(1)

    def _encode(self, bits) -> int:
        # bits ** 8
        encoded_val = 0
        for i in range(EIGHT_NEIGHBORS):
            encoded_val = (encoded_val << bits)  # move 2 bits
            assert self._neighbors[i] < 2 ** bits
            encoded_val += self._neighbors[i]  # add 2 bits
        return encoded_val

    """
    Returns a list of TileConnections possible with the any connection
    """

    def getPossibleNeighborhoods(self) -> List["TileConnection"]:
        i = 0
        while i < EIGHT_NEIGHBORS and self._neighbors[i] != 2:
            i += 1
        if i >= EIGHT_NEIGHBORS:
            return [self.__copy__()]  # no permutations
        ret = []
        neighbors = self._neighbors.copy()
        for j in [0, 1]:
            neighbors[i] = j
            ret.extend(TileConnection(neighbors).getPossibleNeighborhoods())
        return ret

    """
    rotate 90 degrees
    """
    def rot(self) -> "TileConnection":
        neighbors = [0] * EIGHT_NEIGHBORS

        # index of rotating neighbors
        to_swap = [2, 4, 7, 1, 6, 0, 3, 5]  # TODO use enum

        for i in range(EIGHT_NEIGHBORS):
            neighbors[to_swap[i]] = self._neighbors[i]
        return TileConnection(neighbors)

    def xFlip(self) -> "TileConnection":
        neighbors = [0] * EIGHT_NEIGHBORS
        to_swap = [2, 1, 0, 4, 3, 7, 6, 5]  # TODO use enum
        for i in range(EIGHT_NEIGHBORS):
            neighbors[i] = self._neighbors[to_swap[i]]
        return TileConnection(neighbors)

    def yFlip(self) -> "TileConnection":
        neighbors = [0] * EIGHT_NEIGHBORS
        to_swap = [5, 6, 7, 3, 4, 0, 1, 2]  # TODO use enum
        for i in range(EIGHT_NEIGHBORS):
            neighbors[i] = self._neighbors[to_swap[i]]
        return TileConnection(neighbors)

    def _relationToString(self, i: int):
        val = self._neighbors[i]
        return "# E " if val == 0 else ("# F " if val == 1 else "# A ")

    def __str__(self):
        _str = ""
        for i in range(3):
            _str += self._relationToString(i)
        _str += f"#\n{self._relationToString(3)}####{self._relationToString(4)}#\n"
        for i in range(5, EIGHT_NEIGHBORS):
            _str += self._relationToString(i)
        _str += "#\n"
        return _str

    def __eq__(self, other):
        if isinstance(other, TileConnection):
            for i in range(EIGHT_NEIGHBORS):
                if self._neighbors[i] != other._neighbors[i]:
                    return False
            return True
        return NotImplemented

    def __copy__(self):
        return TileConnection(self._neighbors)

    def getNeighbors(self):
        return self._neighbors

    """
    Returns a TileConnection where every ANY connection is FULL
    """

    def getFull(self) -> "TileConnection":
        neighbors = self._neighbors
        return TileConnection([min(n, 1) for n in neighbors])

    def getEmpty(self) -> "TileConnection":
        neighbors = self._neighbors
        return TileConnection([n % 2 for n in neighbors])

    def getInverseNeighborhood(self, button_id: int, default: int = 2) -> "TileConnection":
        """
        Builds the TileConnection a neighbor button sees, given this (center) connection.

        The neighbor at ``button_id`` observes the 8-neighborhood around itself. Each slot is
        filled with the relationship this center tile stores for the tile sitting there, and the
        center itself is looked up at the slot facing button_id (its own relation, mirrored).
        slots that point outside the center's 3x3 grid are set to ``default``.
        """
        if button_id < 0 or button_id >= EIGHT_NEIGHBORS:
            raise ValueError(f"Invalid neighbor ID {button_id}")
        if default < 0 or default > 2:
            raise ValueError(f"Invalid default {default}")
        ret = [default] * EIGHT_NEIGHBORS
        bx, by = NEIGHBOR_OFFSETS[button_id]
        for local_index, (lx, ly) in enumerate(NEIGHBOR_OFFSETS):
            gx, gy = bx + lx, by + ly
            if gx == 0 and gy == 0:
                ret[local_index] = self._neighbors[button_id]
            elif -1 <= gx <= 1 and -1 <= gy <= 1:
                ret[local_index] = self._neighbors[NEIGHBOR_INDEX_BY_OFFSET[(gx, gy)]]
        return TileConnection(ret)

    def setNeighbor(self, neighbor_id, state):
        if state < 0 or state > 2:
            raise ValueError(f"Invalid state {state}")
        if neighbor_id < 0 or neighbor_id >= EIGHT_NEIGHBORS:
            raise ValueError(f"Invalid neighbor ID {neighbor_id}")
        self._neighbors[neighbor_id] = state


"""
def decode(encoded_val: int):
    neighbors = []
    for _ in range(EIGHT_NEIGHBORS):
        neighbors.append(encoded_val & NEIGHBOR_BIT_COMPARATOR)
        encoded_val = encoded_val >> NUM_NEIGHBOR_BITS
    if encoded_val != 0:
        raise ValueError(f"Could not decode {encoded_val}, because it contains too much information")
    neighbors.reverse()
    return TileConnection(neighbors)
"""


def encodeListSmall(tile_connection_list: List[TileConnection]) -> Set[int]:
    ret = set()
    for tc in tile_connection_list:
        ret.add(tc.encodeSmall())
    return ret
