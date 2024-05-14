from typing import TYPE_CHECKING, Any

from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QPainter, QPolygon, QRegion
from PyQt5.QtWidgets import QAbstractButton

from src.images_helper import drawCheckerImage
from src.logic.tile_handler import TileHandler

if TYPE_CHECKING:
    from src.widgets.widget_tile import Tile


class TileConnectionButton(QAbstractButton):
    """
    dir: orientation to the next connection, 0 is up, 2 is right (clockwise)
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._state = 2  # Any
        self._tile = None
        self.setMinimumSize(64, 64)
        self.setMaximumSize(64, 64)

    def paintEvent(self, _e: Any, _qpe: Any = None) -> None:
        qp = QPainter(self)
        size = self.size()

        state_text = "EMPTY" if self._state == 0 else ("FULL" if self._state == 1 else "ANY")
        drawCheckerImage(qp, size.width(), size.height())
        if not self._tile:
            if self._state == 1 or self._state == 2:
                pm = TileHandler.instance().getPixmap(1)
                if self._state == 2:
                    polygon = QPolygon()
                    polygon << QPoint(0, 0) << QPoint(size.width(), size.height()) << QPoint(0, size.height())
                    reg = QRegion(polygon)
                    qp.setClipRegion(reg)
                qp.drawPixmap(0, 0, size.width(), size.height(), pm)
                qp.setClipping(False)
        else:
            pm = self._tile.pixmap()
            qp.drawPixmap(0, 0, size.width(), size.height(), pm)

        qp.drawText(1, size.height() // 2, state_text)
        qp.end()

    def checkStateSet(self):
        return self._state

    def nextCheckState(self):
        self.setState(self._state + 1)

    def setTile(self, tile: "Tile"):
        self._tile = tile
        self.update()

    def setState(self, state):
        self._state = state
        self._state %= 3  # Tri state button
        self.update()
