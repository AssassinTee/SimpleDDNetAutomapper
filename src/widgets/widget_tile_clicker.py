from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui  import QPainter, QImage, QPen, QFont, QColor, QPixmap
from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout

from widgets.widget_tile import Tile
from globals import TILESET_COL, TILESET_ROW, NUM_TILES

class TileClicker(QWidget):
    
    def __init__(self):
        super().__init__()
        self.gridLayout = QGridLayout()
        self.setLayout(self.gridLayout)
    
    def setPixmap(self, pixmap: QPixmap):
        tile_width = pixmap.width()//TILESET_COL
        tile_height = pixmap.height()//TILESET_ROW
        tile_width_float = pixmap.width()/TILESET_COL
        tile_height_float = pixmap.height()/TILESET_ROW
        
        self.tiles = []
        for i in range(NUM_TILES):
            row = i // TILESET_COL
            col = i % TILESET_COL
            tileWidget = Tile(i, width=tile_width, height=tile_height)
            self.tiles.append(tileWidget)
            self.gridLayout.addWidget(tileWidget, row, col)
        
        for i in range(NUM_TILES):
            tile = self.tiles[i]
            
            # yes, there might be gaps due to bad tilesets
            x = int((i % TILESET_COL) * tile_width_float)
            y = int((i // TILESET_ROW) * tile_height_float)
            tile.setPixmap(pixmap.copy(x, y, tile_width, tile_height))
            tile.setScaledContents(False)
            tile.setMaximumSize(128,128)
        