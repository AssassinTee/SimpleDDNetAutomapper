"""A rectangular block of tiles that gets placed as one unit."""
import re
from enum import Enum
from typing import List

from src.globals import TILESET_COL, TILESET_ROW

# A group name becomes an rpp object name. No underscores: rpp's tokenizer splits an identifier on
# '_' and reads each part as its own token, so `big_rock` is two tokens rather than one name.
NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9]*$", re.ASCII)

# rpp's keywords (rpp/include/tokenliterals.hpp) plus the only lowercase globals base.r puts in the
# shared namespace, everything else it exports is PascalCase
RESERVED = frozenset("""
    anchor and array assert automapper bool break continue coord count empty end error false float
    for full function group if index insert int invoke last modulo nested newrule newrun nocopy
    nodefault not notindex null object operator or pos random range return rotate rule string to
    true type warning
    top right bottom left topLeft topRight bottomRight bottomLeft all vertical horizontal this
""".split())


class GroupMode(Enum):
    FILL = "fill"          # only the footprint itself has to be solid
    DECORATE = "decorate"  # the ring around the footprint has to be solid too


class TileGroup:
    def __init__(self, name: str, top_left: int, width: int, height: int,
                 mode: GroupMode = GroupMode.FILL, chance: float = 100.0):
        self.name = name
        self.top_left = top_left
        self.width = width
        self.height = height
        self.mode = mode
        self.chance = chance
        self.validate()

    def validate(self):
        if not NAME_PATTERN.match(self.name):
            raise ValueError(f"'{self.name}' is not a usable group name, letters and digits only "
                             f"and it has to start with a letter — try 'stone3x3'")
        if self.name in RESERVED:
            raise ValueError(f"'{self.name}' is not a usable group name, it means something to rpp already")
        if self.width < 1 or self.height < 1:
            raise ValueError(f"group '{self.name}' has no area")
        # rpp's Rect() rejects index 0, and DDNet treats index 0 as EMPTY anyway
        if self.top_left < 1:
            raise ValueError(f"group '{self.name}' may not start at tile {self.top_left}, tile 0 is always empty")
        if self.column + self.width > TILESET_COL or self.row + self.height > TILESET_ROW:
            raise ValueError(f"group '{self.name}' does not fit on the tileset")
        if not 0 < self.chance <= 100:
            raise ValueError(f"group '{self.name}' has a chance of {self.chance}, expected a percentage above 0")

    @property
    def row(self) -> int:
        return self.top_left // TILESET_COL

    @property
    def column(self) -> int:
        return self.top_left % TILESET_COL

    @property
    def bottom_right(self) -> int:
        return self.top_left + (self.height - 1) * TILESET_COL + (self.width - 1)

    @property
    def area(self) -> int:
        return self.width * self.height

    def tileIds(self) -> List[int]:
        return [self.top_left + y * TILESET_COL + x
                for y in range(self.height)
                for x in range(self.width)]

    def ringOffsets(self) -> List[tuple]:
        """The 8-ring around the footprint, relative to the top left corner, in reading order"""
        return [(x, y)
                for y in range(-1, self.height + 1)
                for x in range(-1, self.width + 1)
                if not (0 <= x < self.width and 0 <= y < self.height)]

    def __repr__(self):
        return f"TileGroup({self.name!r}, {self.top_left}, {self.width}x{self.height}, {self.mode.value})"
