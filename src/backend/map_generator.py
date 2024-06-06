import tempfile

import twmap
import numpy as np
from src.config.app_state import AppState
from pathlib import Path
from src.dialogs.dialog_check_map import CheckMapDialog


class MapGenerator:
    def __init__(self, file_path):
        self._map = twmap.Map.empty("DDNet06")

        solid_map = np.loadtxt("data/debroijn_torus.txt", dtype=np.uint8)
        solid_map = np.pad(solid_map, 1, mode='constant')  # add gap to borders
        height, width = solid_map.shape

        # add layers
        physics_group = self._map.groups.new_physics()
        physics_layer = physics_group.layers.new_game(width, height)

        # add image
        assert AppState.imagePath()
        path = Path(AppState.imagePath()).absolute()
        self._map.images.new_from_file(str(path))

        # set physic tiles
        zeros = np.zeros(solid_map.shape, dtype=np.uint8)
        solid_map_stacked = np.stack([solid_map, zeros], axis=2)
        physics_layer.tiles = solid_map_stacked

        # add tile layer
        tile_layer = physics_group.layers.new_tiles(width, height)
        tile_layer.name = "test"
        tile_layer.image = 0
        tile_layer_map = np.zeros(solid_map_stacked.shape, dtype=np.uint8)

        # TODO twmap doesn't have automappers in the python version yet, so I have to do it manually
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                tile, status = CheckMapDialog.getMapTile(solid_map, x, y)
                if tile:
                    tile_layer_map[y, x, 0] = tile.tile_id
                if status:
                    tile_layer_map[y, x, 1] = MapGenerator._encodeBits(status.h_flip, status.v_flip, status.rot)
        tile_layer.tiles = tile_layer_map

        # save map
        self._map.save(str(file_path))

    def __del__(self):
        # TODO delete map
        pass

    @staticmethod
    def _encodeBits(h_flip: bool, v_flip: bool, rot: bool) -> int:
        ret: int = 0
        ret += (rot << 3)
        ret += (h_flip << 1)
        ret += v_flip
        return ret
