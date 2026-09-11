"""Generates DDNet `.rules` lines."""
from typing import Dict, List, Tuple

from src.globals import EIGHT_NEIGHBORS
from src.backend.tile_status import TileStatus

NeighborhoodEntry = Tuple[int, TileStatus]
NeighborhoodMap = Dict[int, List[NeighborhoodEntry]]

# indexed by bit, and encodeSmall shifts neighbor 0 first, so bit j holds neighbor 7-j
RULE_POS_MAP = {
    0: "1 1",
    1: "0 1",
    2: "-1 1",
    3: "1 0",
    4: "-1 0",
    5: "1 -1",
    6: "0 -1",
    7: "-1 -1",
}


def createRuleLines(neighborhood_map: NeighborhoodMap) -> List[str]:
    rule_list = []
    for i in range(2 ** EIGHT_NEIGHBORS):
        base_tiles = neighborhood_map[i]
        if len(base_tiles) > 0:
            # use first one, TODO: randomize?
            tile_id, tile_status = base_tiles[0]
            placing_rules = []
            for j in range(EIGHT_NEIGHBORS):
                full_neighbor = ((i >> j) & 1) > 0
                str_full = "FULL" if full_neighbor else "EMPTY"
                placing_rules.append(f"Pos {RULE_POS_MAP[j]} {str_full}")
            rule_list.extend([createIndexRule(tile_id, tile_status), *placing_rules])
    return rule_list


def createIndexRule(tile_id: int, tile_status: TileStatus) -> str:
    str_index = f"Index {tile_id}"
    str_x_flip = " XFLIP" if tile_status.x_flip else ""
    str_y_flip = " YFLIP" if tile_status.y_flip else ""
    str_rotate = " ROTATE" if tile_status.rot else ""
    return f"{str_index}{str_x_flip}{str_y_flip}{str_rotate}"
