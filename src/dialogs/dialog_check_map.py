import random
from typing import List, Optional, Tuple

import numpy as np
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QDialog, QGridLayout, QDialogButtonBox, QLabel

from src.logic.tile_status import TileStatus
from src.globals import EIGHT_NEIGHBORS
from src.images_helper import ImageHelper
from src.logic.tile_connection import TileConnection
from src.logic.tile_handler import TileHandler, NeighborhoodEntry
from src.widgets.widget_base_tile import BaseTile


class CheckMapDialog(QDialog):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.setWindowTitle("Check tile configurations")
        self.layout = QGridLayout()
        self.layout.setHorizontalSpacing(0)
        self.layout.setVerticalSpacing(0)

        # load torus
        solid_map = np.loadtxt("data/debroijn_torus.txt", dtype=np.int8)
        height, width = solid_map.shape

        # add stretch in front and after map for central alignment
        self.layout.setRowStretch(0, 1)
        self.layout.setColumnStretch(0, 1)
        self.layout.setRowStretch(height + 1, 1)
        self.layout.setColumnStretch(width + 1, 1)

        # add map tiles into QGridLayout as QLabels
        for map_y in range(height):
            for map_x in range(width):
                grid_y = map_y + 1
                grid_x = map_x + 1

                tile, status = CheckMapDialog._getMapTile(solid_map, map_x, map_y)
                if not tile:
                    tile = QLabel()  # Empty tile
                    if solid_map[map_y, map_x] == 0:
                        tile.setPixmap(ImageHelper.instance().NO_TILE_FOUND_EMPTY)
                    else:
                        tile.setPixmap(ImageHelper.instance().NO_TILE_FOUND)
                else:
                    tile.tile_data.status = status
                tile.setFixedSize(QSize(64, 64))
                self.layout.addWidget(tile, grid_y, grid_x, 1, 1)

        # add ok and cancel button
        q_btn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(q_btn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.layout.addWidget(self.buttonBox, height + 2, 0, 1, width, Qt.AlignHCenter)
        self.setLayout(self.layout)
        self.setModal(True)

    @staticmethod
    def _getMapPixel(solid_map: np.ndarray, x: int, y: int) -> int:
        if x < 0 or y < 0 or x >= solid_map.shape[1] or y >= solid_map.shape[0]:
            """
            return empty tile for out of bounds, I could wrap it tho? hmmmmmmm
            This thing is already a torus, and it's wrapped already by 2 rows/cols, idk
            """
            return 0
        return int(solid_map[y, x])

    @staticmethod
    def _getMapNeighborhood(solid_map: np.ndarray, x: int, y: int) -> List[int]:
        coordinates = {
            0: (0, 0),
            1: (1, 0),
            2: (2, 0),
            3: (0, 1),
            4: (2, 1),
            5: (0, 2),
            6: (1, 2),
            7: (2, 2)
        }
        neighbors = [CheckMapDialog._getMapPixel(solid_map, x + coordinates[i][0] - 1, y + coordinates[i][1] - 1)
                     for i in range(EIGHT_NEIGHBORS)]
        return neighbors

    @staticmethod
    def _getMapTile(solid_map: np.ndarray, x, y) -> Tuple[Optional[BaseTile], Optional[TileStatus]]:
        if solid_map[y, x] == 0:
            return None, None  # TODO this isn't true
        neighbors = CheckMapDialog._getMapNeighborhood(solid_map, x, y)
        tc = TileConnection(neighbors)
        tile_id_list: List[NeighborhoodEntry] = TileHandler.instance().findTiles(tc)
        if len(tile_id_list):
            rand_tile_id = random.randint(0, len(tile_id_list) - 1)  # I could make more sure that every tile is used
            tile_id, status = tile_id_list[rand_tile_id]
            return TileHandler.instance().getTile(tile_id), status
        return None, None
