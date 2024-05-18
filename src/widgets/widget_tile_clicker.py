from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QGridLayout

from src.globals import TILESET_COL, TILESET_ROW, NUM_TILES
from src.widgets.widget_tile import Tile


class TileClicker(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.gridLayout = QGridLayout()
        self.gridLayout.setHorizontalSpacing(0)
        self.gridLayout.setVerticalSpacing(0)
        self.setLayout(self.gridLayout)
        self.tiles = []

    def setPixmap(self, pixmap: QPixmap):
        tile_width = pixmap.width() // TILESET_COL
        tile_height = pixmap.height() // TILESET_ROW
        tile_width_float = pixmap.width() / TILESET_COL
        tile_height_float = pixmap.height() / TILESET_ROW

        self.tiles = []

        for i in range(NUM_TILES):
            row = i // TILESET_COL
            col = i % TILESET_COL
            tile_widget = Tile(i, width=tile_width, height=tile_height)
            self.tiles.append(tile_widget)
            self.gridLayout.addWidget(tile_widget, row + 1, col + 1)

        # handle all tiles except 0, handle tile 0 separately
        for i in range(1, NUM_TILES):
            tile = self.tiles[i]

            # yes, there might be gaps due to bad tilesets
            x = int((i % TILESET_COL) * tile_width_float)
            y = int((i // TILESET_ROW) * tile_height_float)
            tile.setPixmap(pixmap.copy(x, y, tile_width, tile_height))

        self.gridLayout.setRowStretch(0, 1)
        self.gridLayout.setColumnStretch(0, 1)
        self.gridLayout.setRowStretch(TILESET_ROW + 1, 1)
        self.gridLayout.setColumnStretch(TILESET_COL + 1, 1)
