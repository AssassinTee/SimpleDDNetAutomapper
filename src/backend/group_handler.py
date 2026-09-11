"""
Holds the tile groups the user defined. Separate from TileHandler, which is indexed by
neighborhood and has nothing to say about multi-tile blocks.
"""
from typing import Dict, List, Optional

from src.backend.tile_group import GroupMode, TileGroup


class GroupHandler:
    _instance = None

    def __init__(self):
        raise RuntimeError('Call instance() instead')

    def _init(self):
        self.groups: Dict[str, TileGroup] = {}

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._instance._init()
        return cls._instance

    def addGroup(self, top_left: int, width: int, height: int, mode: GroupMode = GroupMode.FILL,
                 chance: float = 100.0, name: Optional[str] = None) -> TileGroup:
        group = TileGroup(name or self.nextName(), top_left, width, height, mode, chance)
        if group.name in self.groups:
            raise ValueError(f"A group named '{group.name}' already exists")

        # every group needs its own anchor tile, and sharing tiles would make the claims ambiguous
        taken = {tile_id: other.name for other in self.groups.values() for tile_id in other.tileIds()}
        clash = next((taken[tile_id] for tile_id in group.tileIds() if tile_id in taken), None)
        if clash:
            raise ValueError(f"Those tiles already belong to '{clash}'")

        # the list is a priority order and the first group that fits a spot keeps it, so the group
        # the user just drew goes to the front where they can watch it work
        self.groups = {group.name: group, **self.groups}
        return group

    def moveGroup(self, name: str, offset: int) -> bool:
        names = list(self.groups)
        old = names.index(name)
        new = max(0, min(len(names) - 1, old + offset))
        if old == new:
            return False
        names.insert(new, names.pop(old))
        self.groups = {group_name: self.groups[group_name] for group_name in names}
        return True

    def renameGroup(self, old_name: str, new_name: str):
        if old_name == new_name:
            return
        if new_name in self.groups:
            raise ValueError(f"A group named '{new_name}' already exists")
        group = self.groups[old_name]
        group.name = new_name
        try:
            group.validate()
        except ValueError:
            group.name = old_name
            raise
        # rebuilt in place rather than re-added, the order of this dict is the order of the rules
        self.groups = {(new_name if name == old_name else name): value
                       for name, value in self.groups.items()}

    def groupAt(self, tile_id: int) -> Optional[TileGroup]:
        return next((group for group in self.groups.values() if tile_id in group.tileIds()), None)

    def nextName(self) -> str:
        # no underscore before the number: rpp reads `group_0` as the keyword `group` plus `_0`
        i = 0
        while f"group{i}" in self.groups:
            i += 1
        return f"group{i}"

    def removeGroup(self, name: str):
        self.groups.pop(name, None)

    def getGroups(self) -> List[TileGroup]:
        return list(self.groups.values())

    def setGroups(self, groups: List[TileGroup]):
        self.groups = {group.name: group for group in groups}

    def reset(self):
        self._init()
