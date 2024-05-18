from src.globals import EIGHT_NEIGHBORS, NUM_NEIGHBOR_BITS, NUM_NEIGHBOR_STATES, NEIGHBOR_BIT_COMPARATOR
from typing import List, Set


class TileConnection:
    def __init__(self, neighbors: list):
        if len(neighbors) != EIGHT_NEIGHBORS:
            raise ValueError(f"Neighbors are not {EIGHT_NEIGHBORS}")
        for i in range(EIGHT_NEIGHBORS):
            if neighbors[i] < 0 or neighbors[i] >= NUM_NEIGHBOR_STATES:
                raise ValueError(f"neighbor[{i}] not in range [0 2]")
        self._neighbors = neighbors

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

    def getPermutations(self) -> List["TileConnection"]:
        i = 0
        while i < EIGHT_NEIGHBORS and self._neighbors[i] != 2:
            i += 1
        if i >= EIGHT_NEIGHBORS:
            return [self.__copy__()]  # no permutations
        ret = []
        neighbors = self._neighbors.copy()
        for j in [0, 1]:
            neighbors[i] = j
            ret.extend(TileConnection(neighbors).getPermutations())
        return ret

    """
    rotates 45 degree
    """

    def rotate45(self) -> "TileConnection":
        neighbors = [0] * EIGHT_NEIGHBORS

        # index of rotating neighbors
        to_swap = [3, 0, 1, 5, 2, 6, 7, 4]  # TODO use enum

        for i in range(EIGHT_NEIGHBORS):
            neighbors[i] = self._neighbors[to_swap[i]]
        return TileConnection(neighbors)

    def rotate90(self) -> "TileConnection":
        return self.rotate45().rotate45()  # yes, this could be optimized

    def vFlip(self) -> "TileConnection":
        neighbors = [0] * EIGHT_NEIGHBORS
        to_swap = [2, 1, 0, 4, 3, 7, 6, 5]  # TODO use enum
        for i in range(EIGHT_NEIGHBORS):
            neighbors[i] = self._neighbors[to_swap[i]]
        return TileConnection(neighbors)

    def hFlip(self) -> "TileConnection":
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
        return TileConnection(self._neighbors.copy())

    def getNeighbors(self):
        return self._neighbors

    """
    Returns a TileConnection where every ANY connection is FULL
    """

    def getFull(self) -> "TileConnection":
        neighbors = self._neighbors.copy()
        return TileConnection([min(n, 1) for n in neighbors])

    def getEmpty(self) -> "TileConnection":
        neighbors = self._neighbors.copy()
        return TileConnection([n % 2 for n in neighbors])

    def setNeighbor(self, neighbor_id, state):
        if state < 0 or state > 2:
            return ValueError(f"Invalid state {state}")
        if neighbor_id < 0 or neighbor_id > EIGHT_NEIGHBORS:
            return ValueError(f"Invalid neighbor ID {neighbor_id}")
        self._neighbors[neighbor_id] = state


def decode(encoded_val: int):
    neighbors = []
    for _ in range(EIGHT_NEIGHBORS):
        neighbors.append(encoded_val & NEIGHBOR_BIT_COMPARATOR)
        encoded_val = encoded_val >> NUM_NEIGHBOR_BITS
    if encoded_val != 0:
        raise ValueError(f"Could not decode {encoded_val}, because it contains too much information")
    neighbors.reverse()
    return TileConnection(neighbors)


def encodeListSmall(tile_connection_list: List[TileConnection]) -> Set[int]:
    ret = set()
    for tc in tile_connection_list:
        ret.add(tc.encodeSmall())
    return ret
