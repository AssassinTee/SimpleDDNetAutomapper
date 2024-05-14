from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import Qt
from dialogs.dialog_tile_settings import TileSettingsDialog
from logic.tile_data import TileData
from logic.tile_handler import TileHandler
from typing import Optional
from images_helper import drawCheckerImage

class Tile(QLabel):
    def __init__(self, id: int, width=64, height=64) -> None:
        super().__init__()
        self.id: int = id
        self.width = width
        self.height = height
            
        self.mousePressEvent = self.openDialog
        self.hovered = False
        self.selected = False
        self.dialog = TileSettingsDialog(self)
        self.tile_data: Optional[TileData] = None
        if id == 0:
            self.lock = True
        else:
            self.setMouseTracking(True)
            self.lock = False
        TileHandler.instance().addTile(self)

    def getID(self) -> int:
        return self.id
    
    def paintEvent(self, e):
        qp = QPainter(self)
        drawCheckerImage(qp, self.width, self.height)
        qp.end()
        super().paintEvent(e)
        if self.pixmap():
            qp = QPainter(self)
            self.paintPixmapExists(qp)
            qp.end()
            
    def paintPixmapExists(self, qp: QPainter):
        if self.lock:
            # draw locked emoji
            qp.setPen(QPen(QColor(40, 40, 40, 255), 10))
            qp.drawText(self.width - 20, self.height-20, 20, 20, Qt.AlignVCenter, "🔒")
        else:    
            if self.hovered or self.selected:
                qp.fillRect(0, 0, self.width - 1, self.height - 1, QColor(255, 255, 255, 100))
                
            if self.tile_data:
                qp.setPen(QPen(QColor(0, 255, 0, 255), 10))
                qp.drawText(self.width - 20, self.height-20, 20, 20, Qt.AlignVCenter, "✔️")
            
        # draw outline
        qp.setPen(QPen(QColor(0, 0, 0, 255), 1))
        qp.drawRect(0, 0, self.width - 1, self.height - 1)
            
    def openDialog(self, e):
        # one does not simply configure locked tiles
        if self.lock:
            return
        
        # mark tile as selected
        self.selected = True
        self.update()
        
        # configure tile, this may take a while
        # update tile data in dialog
        # use a copy, because if you press cancel, this should still store the original values
        if self.tile_data:
            self.dialog.setTileData(self.tile_data.__copy__())
        ret = self.dialog.exec()
        # ok pressed
        if ret == 1:
            # update tile data in handler
            self.tile_data = self.dialog.getTileData()
            TileHandler.instance().updateTileRelations(self)
            
        # mark tile as deselected after dialog
        self.selected = False
        self.update()
        print(ret)
        
    def enterEvent(self, event):
        self.hovered = True
        self.update()
    
    def leaveEvent(self, event):
        self.hovered = False
        self.update()
        
