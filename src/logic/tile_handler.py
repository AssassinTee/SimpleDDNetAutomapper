from typing import List, Dict, TYPE_CHECKING, Set

from src.globals import EIGHT_NEIGHBORS

if TYPE_CHECKING:
    from src.widgets.widget_tile import Tile


class TileHandler:
    _instance = None

    def __init__(self):
        raise RuntimeError('Call instance() instead')

    def _init(self):
        # Tile Storage:
        # contains encoded neighbor relation and points to Tile, can have multiple tiles
        # different encodings may contain the same tile as well
        # Reverse Storage:
        # maps tile ID to storage locations in order to allow for removals
        storage_size = 2 ** EIGHT_NEIGHBORS
        self.relation_storage: Dict[int, List[int]] = {}
        for i in range(storage_size):
            self.relation_storage[i] = []
        self.reverse_relation_storage: Dict[int, List[int]] = {}
        self.id_map: Dict[int, "Tile"] = {}

    def addTileRelations(self, tile: "Tile"):
        # A tile can have multiple relations due to rotation and flipping
        permutations: Set[int] = tile.tile_data.getPermutations()
        for neighbor_enc in permutations:
            # add relation to storage
            if tile.getID() not in self.relation_storage[neighbor_enc]:
                self.relation_storage[neighbor_enc].append(tile.getID())

            # add relation to reverse storage
            if tile.getID() not in self.reverse_relation_storage:
                self.reverse_relation_storage[tile.getID()] = []
            if neighbor_enc not in self.reverse_relation_storage[tile.getID()]:
                self.reverse_relation_storage[tile.getID()].append(neighbor_enc)

    """
    removes tile relations
    """

    def removeTileRelations(self, tile_id: int):
        # tile not in or already removed
        if tile_id not in self.reverse_relation_storage:
            return

        # remove from encodings
        for neighbor_enc in self.reverse_relation_storage[tile_id]:
            self.relation_storage[neighbor_enc].remove(tile_id)

        # remove from reverse map
        del self.reverse_relation_storage[tile_id]

    def updateTileRelations(self, tile: "Tile"):
        self.removeTileRelations(tile.getID())
        self.addTileRelations(tile)

    def addTile(self, tile: "Tile"):
        self.id_map[tile.tile_id] = tile

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._instance._init()
        return cls._instance

    def getPixmap(self, tile_id: int):
        if tile_id not in self.id_map:
            return ValueError(f"ID {tile_id} not known")
        return self.id_map[tile_id].pixmap()
