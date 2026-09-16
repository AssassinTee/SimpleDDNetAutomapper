import json
from typing import Dict, List, Optional, Sequence

from src.globals import NUM_TILES
from src.backend.tile_connection import TileConnection
from src.backend.tile_data import TileData
from src.backend.tile_group import GroupMode, TileGroup
from src.backend.tile_modificators import TileMods
from src.backend.tile_status import TileStatus

SERIALIZATION_VERSION = 1


class Blueprint:
    def __init__(self, tiles: Dict[int, TileData], image: Optional[str] = None,
                 groups: Optional[Sequence[TileGroup]] = None):
        self.tiles = tiles
        self.image = image
        self.groups: List[TileGroup] = list(groups or [])


def dumps(blueprint: Blueprint) -> str:
    tiles = [json.dumps(_tileToDict(tile_id, blueprint.tiles[tile_id])) for tile_id in sorted(blueprint.tiles)]
    groups = [json.dumps(_groupToDict(group)) for group in blueprint.groups]

    return ("{\n"
            f'  "version": {SERIALIZATION_VERSION},\n'
            f'  "image": {json.dumps(blueprint.image)},\n'
            f'  "tiles": {_jsonBlock(tiles)},\n'
            f'  "groups": {_jsonBlock(groups)}\n'
            "}\n")


def _jsonBlock(entries: List[str]) -> str:
    if not entries:
        return "[]"
    return "[\n" + ",\n".join(f"    {entry}" for entry in entries) + "\n  ]"


def loads(text: str) -> Blueprint:
    raw = json.loads(text)
    if raw["version"] != SERIALIZATION_VERSION:
        raise ValueError(f"Unsupported blueprint version {raw['version']}, expected {SERIALIZATION_VERSION}")

    tiles: Dict[int, TileData] = {}
    for entry in raw["tiles"]:
        tile_id = entry["id"]
        if not 0 <= tile_id < NUM_TILES:
            raise ValueError(f"Tile ID {tile_id} out of range")
        if tile_id in tiles:
            raise ValueError(f"Duplicate tile ID {tile_id}")
        tiles[tile_id] = _tileFromDict(entry)

    groups = [_groupFromDict(entry) for entry in raw["groups"]]
    names = [group.name for group in groups]
    if len(set(names)) != len(names):
        raise ValueError("Duplicate group name")

    return Blueprint(tiles, raw["image"], groups)


def _groupToDict(group: TileGroup) -> dict:
    return {
        "name": group.name,
        "top_left": group.top_left,
        "width": group.width,
        "height": group.height,
        "mode": group.mode.value,
        "chance": group.chance,
    }


def _groupFromDict(entry: dict) -> TileGroup:
    return TileGroup(entry["name"], entry["top_left"], entry["width"], entry["height"],
                     GroupMode(entry["mode"]), entry["chance"])


def _tileToDict(tile_id: int, tile_data: TileData) -> dict:
    mods: TileMods = tile_data.mods
    return {
        "id": tile_id,
        "con": tile_data.con.getNeighbors(),
        "chance": tile_data.chance,
        "mods": {
            "x_flip": mods.can_x_flip,
            "y_flip": mods.can_y_flip,
            "rot": mods.can_rot,
            "empty": tile_data.status.empty,
        },
    }


def _tileFromDict(entry: dict) -> TileData:
    mods = entry["mods"]

    status = TileStatus()
    status.empty = mods["empty"]

    return TileData(TileConnection(entry["con"]),
                    status,
                    TileMods(can_x_flip=mods["x_flip"], can_y_flip=mods["y_flip"], can_rot=mods["rot"]),
                    entry["chance"])
