from PyQt5.QtWidgets import QAbstractButton
from PyQt5.QtCore import QPointF, QPoint
from PyQt5.QtGui import QPainter, QPen, QTransform, QColor, QPolygon, QRegion
from images_helper import drawCheckerImage
from logic.tile_handler import TileHandler
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from widgets.widget_tile import Tile
    
class TileConnectionButton(QAbstractButton):
    """
    dir: orientation to the next connection, 0 is up, 2 is right (clockwise)
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.state = 2  # Any
        self._tile = None
        self.setMinimumSize(64,64)
        self.setMaximumSize(64,64)
    
    def paintEvent(self, e):
        qp = QPainter(self)
        size = self.size()

        stateText = "EMPTY" if self.state == 0 else ("FULL" if self.state == 1 else "ANY")
        drawCheckerImage(qp, size.width(), size.height())
        if not self._tile:
            if self.state == 1 or self.state == 2:
                pm = TileHandler.instance().getPixmap(1)
                if self.state == 2:
                    polygon = QPolygon()
                    polygon << QPoint(0, 0) << QPoint(size.width(),size.height()) << QPoint(0,size.height())
                    reg = QRegion(polygon)
                    qp.setClipRegion(reg)
                qp.drawPixmap(0, 0, size.width(), size.height(), pm)
                qp.setClipping(False)
        else:
            pm = self._tile.pixmap()
            qp.drawPixmap(0, 0, size.width(), size.height(), pm)
            
        qp.drawText(1, size.height()//2, stateText)
        qp.end()
        
        
    
    def checkStateSet(self):
        return self.state
    
    def nextCheckState(self):
        self.state +=1
        self.state %=3  # Tri state button
        self.update()
        
    def setTile(self, tile: "Tile"):
        self._tile = tile
        self.update()
    