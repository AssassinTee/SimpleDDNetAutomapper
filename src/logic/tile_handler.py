from typing import List, Dict, TYPE_CHECKING, Set

from src.globals import EIGHT_NEIGHBORS
from src.logic.tile_connection import TileConnection
from src.logic.tile_data import TileData

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
        self.tile_data_storage: Dict[int, TileData] = {}
        self.id_map: Dict[int, "Tile"] = {}

    def addTileRelations(self, tile: "Tile"):
        # A tile can have multiple relations due to rotation and flipping
        permutations: Set[int] = tile.tile_data.getPermutations()
        for neighbor_enc in permutations:
            # add relation to storage
            if tile.getID() not in self.relation_storage[neighbor_enc]:
                self.relation_storage[neighbor_enc].append(tile.getID())

        # add relation to reverse storage
        self.tile_data_storage[tile.getID()] = tile.tile_data

    """
    removes tile relations
    """

    def removeTileRelations(self, tile_id: int):
        # tile not in or already removed
        if tile_id not in self.tile_data_storage:
            return

        # remove from encodings
        permutations: Set[int] = self.tile_data_storage[tile_id].getPermutations()
        for neighbor_enc in permutations:
            self.relation_storage[neighbor_enc].remove(tile_id)

        # remove from reverse map
        del self.tile_data_storage[tile_id]

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
    
    def findTiles(self, tile_connection: TileConnection) -> List[int]:
        tile_connections: List[TileConnection] = tile_connection.getPermutations()
        ret = []
        for con in tile_connections:
            con_enc = con.encodeSmall()
            assert con_enc in self.relation_storage
            ret.extend(self.relation_storage[con_enc])
        return ret
    
    def getTile(self, tile_id: int) -> "Tile":
        if tile_id not in self.id_map:
            raise ValueError(f"Unknown tile ID {tile_id}")
        return self.id_map[tile_id]
            
        
