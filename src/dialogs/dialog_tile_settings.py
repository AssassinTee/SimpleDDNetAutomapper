from PyQt5.QtWidgets import QDialog, QGridLayout, QDialogButtonBox
from PyQt5.QtCore import Qt
from buttons.button_tile_connection import TileConnectionButton
from logic.tile_data import TileData
from logic.tile_connection import TileConnection
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from widgets.widget_tile import Tile


class TileSettingsDialog(QDialog):
    def __init__(self, tile: "Tile", parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Configure Tile")
        self.layout = QGridLayout()
        self.layout.setHorizontalSpacing(0)
        self.layout.setVerticalSpacing(0)
        self.buttons = []
        for i in range(9):
            widget = TileConnectionButton(self)
            self.layout.addWidget(widget, i//3, i%3, 1, 1, Qt.AlignVCenter)
            if i == 4:
                self.center = widget
            else:
                self.buttons.append(widget)
        self.center.setTile(tile)
        self.tile = tile

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.layout.addWidget(self.buttonBox, 4, 3)
        self.setLayout(self.layout)
        
        self.setModal(True)
        # TODO calculate smarter values with the tile itself
        self.tile_data = TileData(TileConnection([2] * 8), False, False, False, False)
        
    def getTileData(self):
        return self.tile_data
    
    def setTileData(self, data: TileData):
        self.tile_data = data
        
        # update button states
        for i, button_state in enumerate(self.tile_data.con._neighbors):
            self.buttons[i].setState(button_state)
        
        