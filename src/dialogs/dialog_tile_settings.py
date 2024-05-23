import random
from functools import cache
from typing import TYPE_CHECKING, List, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QGridLayout, QDialogButtonBox

from src.buttons.button_tile_connection import TileConnectionButton
from src.buttons.button_tile_connection_center import TileConnectionCenterButton
from src.globals import EIGHT_NEIGHBORS
from src.backend.tile_connection import TileConnection
from src.backend.tile_data import TileData
from src.backend.tile_handler import TileHandler
from src.backend.tile_status import TileStatus
from src.backend.tile_modificators import TileMods

if TYPE_CHECKING:
    from src.widgets.widget_tile import Tile


class TileSettingsDialog(QDialog):

    def __init__(self, tile: "Tile", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configure Tile")
        self.layout = QGridLayout()
        self.layout.setHorizontalSpacing(0)
        self.layout.setVerticalSpacing(0)

        # add before and after buttons for central alignment
        for stretch_index in [0, 5]:
            self.layout.setRowStretch(stretch_index, 1)
            self.layout.setColumnStretch(stretch_index, 1)

        # add 3x3 buttons
        self.buttons: List[TileConnectionButton] = []
        for i in range(9):
            if i == 4:
                widget = TileConnectionCenterButton(tile, i, self)
                self.center = widget
                widget.signal_emitter.modification_signal.connect(self.onModificationChange)
            else:
                widget = TileConnectionButton(len(self.buttons), self)
                self.buttons.append(widget)
                widget.signal_emitter.neighbor_signal.connect(self.onConnectionButtonClick)
            self.layout.addWidget(widget, i // 3 + 1, i % 3 + 1, 1, 1)

        # self.center.setTile(tile)
        # self.center.setMain()
        self.tile = tile

        q_btn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel

        self.buttonBox = QDialogButtonBox(q_btn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.layout.addWidget(self.buttonBox, 6, 0, 1, 6, Qt.AlignmentFlag.AlignHCenter)
        self.setLayout(self.layout)

        self.setModal(True)
        # TODO calculate smarter values with the tile itself
        self._tile_data = TileData(TileConnection([2] * 8), TileStatus(), TileMods(False, False, False))

    def getTileData(self):
        return self._tile_data.__copy__()

    def setTileData(self, data: TileData):
        self._tile_data = data.__copy__()

        # update button states
        for i, button_state in enumerate(self._tile_data.con.getNeighbors()):
            self.buttons[i].setState(button_state)

        # update tiles
        for i in range(EIGHT_NEIGHBORS):
            self._updateTile(i)

    def onConnectionButtonClick(self, button_id: int):
        # goal: update tile after a button was clicked
        # find TileConnections, then ask handler if any tiles exist
        self._updateTileData(button_id)  # update tile data
        self._updateTile(button_id)  # update own tile

        # update neighbor tiles
        neighbor_buttons = self._getNeighborButtons(button_id)
        for i in range(EIGHT_NEIGHBORS):
            if neighbor_buttons[i] is not None:
                self._updateTile(i)

    def onModificationChange(self, modification: int, value: bool):
        match modification:
            case 0:
                self._tile_data.mods.can_v_flip = value
                return
            case 1:
                self._tile_data.mods.can_h_flip = value
                return
            case 2:
                self._tile_data.mods.can_rot = value
                return
            case 3:
                self._tile_data.status.empty = value
                return
        raise ValueError(f"Modification {modification} unknown")

    def _updateTileData(self, button_id: int):
        state = self.buttons[button_id].checkStateSet()
        self._tile_data.con.setNeighbor(button_id, state)

    def _updateTile(self, button_id: int):
        neighbors = [1] * EIGHT_NEIGHBORS  # all empty (for now) TODO change view with button
        neighbor_buttons = self._getNeighborButtons(button_id)
        for i in range(EIGHT_NEIGHBORS):
            if neighbor_buttons[i] is not None:
                neighbors[i] = self._tile_data.con.getNeighbors()[neighbor_buttons[i]]
        con = TileConnection(neighbors)

        tile_connection = con.getEmpty()
        tile_id_list = TileHandler.instance().findTiles(tile_connection)
        if len(tile_id_list):
            # yay, I found a tile that connects in this location
            # use a random one, because this shouldn't matter
            rand_tile = random.randint(0, len(tile_id_list) - 1)
            tile_id, _ = tile_id_list[rand_tile]
            tile = TileHandler.instance().getTile(tile_id)
            self.buttons[button_id].setTile(tile, False)
        else:  # No tile? reset
            self.buttons[button_id].setTile(None, False)

    @staticmethod
    @cache
    def _getNeighborButtons(button_id) -> List[Optional[int]]:
        """
        returns the 8 neighborhood of a button with button_id.
        If there is no neigbor in the 8-neighbood, None is put in so the location is still known
        
        Examples:
        
        Eight neigborhood of button 0:
        # # #
        # 0 1
        # 3 #
        >>> [None, None, None, None, 1, None, 3, None]
        """
        neighbor_hood = [
            [None, None, None, None, None],
            [None, 0, 1, 2, None],
            [None, 3, None, 4, None],
            [None, 5, 6, 7, None],
            [None, None, None, None, None],
        ]

        def _find_index(num):
            for by, row in enumerate(neighbor_hood):
                for bx, value in enumerate(row):
                    if value == num:
                        return bx, by
            raise ValueError(f"{num} not found")

        button_x, button_y = _find_index(button_id)
        ret = []
        for y in [-1, 0, 1]:
            for x in [-1, 0, 1]:
                if x == 0 and y == 0:  # ignore middle
                    continue
                ret.append(neighbor_hood[y + button_y][x + button_x])
        assert len(ret) == 8
        return ret
