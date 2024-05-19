from typing import List, Dict, TYPE_CHECKING, Tuple

from PyQt6.QtGui import QPixmap

from src.globals import EIGHT_NEIGHBORS
from src.logic.tile_connection import TileConnection
from src.logic.tile_status import TileStatus
from src.widgets.widget_base_tile import BaseTile

if TYPE_CHECKING:
    from src.widgets.widget_tile import Tile

NeighborhoodEntry = Tuple[int, TileStatus]


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
        # small_enc -> tile_id
        self.neighborhood_map: Dict[int, List[NeighborhoodEntry]] = {}
        for i in range(storage_size):
            self.neighborhood_map[i] = []

        self.tile_id_map: Dict[int, BaseTile] = {}

        # stores simply all pixmaps for a tile_id
        self.pix_map: Dict[int, QPixmap] = {}

    def addTileToStorage(self, tile: BaseTile):
        if tile.tile_data is None:
            raise ValueError("Tile data is none")
        tile_states = tile.tile_data.getAllPossibleTileStates()
        for tile_connection, tile_status in tile_states:
            enc_value = tile_connection.encodeSmall()

            entry: NeighborhoodEntry = (tile.tile_id, tile_status)
            self.neighborhood_map[enc_value].append(entry)  # add tuple, tile with configuration

        self.tile_id_map[tile.getID()] = tile.__copy__()

    def removeTileFromStorage(self, tile_id: int):
        # tile not in or already removed
        if tile_id not in self.tile_id_map:
            return
        tile = self.tile_id_map[tile_id]

        # remove tile from neighborhood map
        tile_states = tile.tile_data.getAllPossibleTileStates()
        for tile_connection, tile_status in tile_states:
            enc_value = tile_connection.encodeSmall()
            to_delete = []
            for index, (entry_tile_id, _) in enumerate(self.neighborhood_map[enc_value]):
                if entry_tile_id == tile_id:
                    to_delete.append(index)

            # reverse, because the indices change with each deletion, this bug was ugly
            to_delete.reverse()
            for entry_tile_id in to_delete:
                del self.neighborhood_map[enc_value][entry_tile_id]

        # remove from tile id map
        del self.tile_id_map[tile_id]

    def updateTileStorage(self, tile: BaseTile):
        self.removeTileFromStorage(tile.tile_id)
        self.addTileToStorage(tile)

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._instance._init()
        return cls._instance

    def addPixmap(self, tile: BaseTile):
        if tile.tile_id in self.pix_map:
            raise ValueError(f"ID {tile.tile_id} already in pixmap")  # no overwrite by design
        if tile.pixmap().isNull():
            raise ValueError("Pixmap is empty")
        self.pix_map[tile.tile_id] = tile.pixmap()

    def getPixmap(self, tile_id: int):
        if tile_id not in self.pix_map:
            raise ValueError(f"ID {tile_id} not known")
        return self.pix_map[tile_id]

    def findTiles(self, tile_connection: TileConnection) -> List[NeighborhoodEntry]:
        """
        Returns all tiles, that match a neighborhood
        """
        tile_connections: List[TileConnection] = tile_connection.getPossibleNeighborhoods()
        ret = []
        for con in tile_connections:
            con_enc = con.encodeSmall()
            # assert con_enc in self.neighborhood_map
            ret.extend(self.neighborhood_map[con_enc])
        return ret

    def getTile(self, tile_id: int) -> BaseTile:
        if tile_id not in self.tile_id_map:
            raise ValueError(f"Unknown tile ID {tile_id}")
        return self.tile_id_map[tile_id].__copy__()
