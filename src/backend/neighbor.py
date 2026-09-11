"""
The 8-neighborhood of a tile, defined once. Everything that used to carry its own copy of this
ordering — the flip and rotation swap tables, the `.rules` Pos offsets, the rpp position names, the
dialog's button grid, the tileset scan — derives it from here instead.
"""
from enum import IntEnum
from typing import Optional, Tuple


class Neighbor(IntEnum):
    """Reading order around the center tile, y grows downward."""
    TOP_LEFT = 0
    TOP = 1
    TOP_RIGHT = 2
    LEFT = 3
    RIGHT = 4
    BOTTOM_LEFT = 5
    BOTTOM = 6
    BOTTOM_RIGHT = 7

    @property
    def offset(self) -> Tuple[int, int]:
        grid_pos = self + 1 if self >= Neighbor.RIGHT else int(self)  # the center has no index
        return grid_pos % 3 - 1, grid_pos // 3 - 1

    @property
    def rppName(self) -> str:
        return _RPP_NAMES[self]

    @property
    def bit(self) -> int:
        # TileConnection.encodeSmall() shifts neighbor 0 in first, so neighbor i ends up in bit 7-i
        return len(Neighbor) - 1 - self

    def rot(self) -> "Neighbor":
        x, y = self.offset
        return Neighbor.at(-y, x)

    def xFlip(self) -> "Neighbor":
        x, y = self.offset
        return Neighbor.at(-x, y)

    def yFlip(self) -> "Neighbor":
        x, y = self.offset
        return Neighbor.at(x, -y)

    @staticmethod
    def at(x: int, y: int) -> Optional["Neighbor"]:
        """The neighbor sitting at that offset, or None for the center and anything further out."""
        return _BY_OFFSET.get((x, y))


_RPP_NAMES = ("topLeft", "top", "topRight", "left", "right", "bottomLeft", "bottom", "bottomRight")
_BY_OFFSET = {neighbor.offset: neighbor for neighbor in Neighbor}
