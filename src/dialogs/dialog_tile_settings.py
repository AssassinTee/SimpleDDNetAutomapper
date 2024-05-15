from PyQt5.QtWidgets import QDialog, QGridLayout, QDialogButtonBox
from PyQt5.QtCore import Qt
from src.buttons.button_tile_connection import TileConnectionButton
from src.buttons.button_tile_connection_center import TileConnectionCenterButton
from src.logic.tile_data import TileData
from src.logic.tile_connection import TileConnection
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.widgets.widget_tile import Tile


class TileSettingsDialog(QDialog):
    # noinspection PyUnresolvedReferences
    def __init__(self, tile: "Tile", parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Configure Tile")
        self.layout = QGridLayout()
        self.layout.setHorizontalSpacing(0)
        self.layout.setVerticalSpacing(0)

        # add before and after buttons for central alignment
        for stretch_index in [0, 5]:
            self.layout.setRowStretch(stretch_index, 1)
            self.layout.setColumnStretch(stretch_index, 1)

        # add 3x3 buttons
        self.buttons = []
        for i in range(9):
            if i == 4:
                widget = TileConnectionCenterButton(tile, self)
                self.center = widget
            else:
                widget = TileConnectionButton(self)
                self.buttons.append(widget)
            self.layout.addWidget(widget, i // 3 + 1, i % 3 + 1, 1, 1)

        #self.center.setTile(tile)
        #self.center.setMain()
        self.tile = tile

        q_btn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(q_btn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.layout.addWidget(self.buttonBox, 6, 0, 1, 6, Qt.AlignHCenter)
        self.setLayout(self.layout)

        self.setModal(True)
        # TODO calculate smarter values with the tile itself
        self.tile_data = TileData(TileConnection([2] * 8), False, False, False, False)

    def getTileData(self):
        return self.tile_data

    def setTileData(self, data: TileData):
        self.tile_data = data

        # update button states
        for i, button_state in enumerate(self.tile_data.con.getNeighbors()):
            self.buttons[i].setState(button_state)
