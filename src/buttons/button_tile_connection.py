from typing import TYPE_CHECKING, Any, Optional

from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QPainter, QPolygon, QRegion, QPixmap, QColor, QPen
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
        self._num_states = 3
        self._tile = None
        self._main = False
        self.setMinimumSize(128, 128)
        self.setMaximumSize(128, 128)

    def paintEvent(self, _e: Any, _qpe: Any = None) -> None:
        qp = QPainter(self)

        # draw background
        drawCheckerImage(qp, self.size().width(), self.size().height())

        self._paintTile(qp)
        self._paintOutline(qp)
        self._paintText(qp)
        qp.end()

    def _paintTile(self, qp: QPainter):
        size = self.size()
        # clip region for ANY in order to show state between empty and full
        if not self._main and self._state == 2:
            polygon = QPolygon()
            polygon << QPoint(0, 0) << QPoint(size.width(), size.height()) << QPoint(0, size.height())
            reg = QRegion(polygon)
            qp.setClipRegion(reg)

        # draw tile
        pm = self._findPixmap()
        if pm:
            qp.drawPixmap(0, 0, size.width(), size.height(), pm)
        qp.setClipping(False)

    # will be overwritten
    def _paintOutline(self, qp: QPainter):
        return

    def _paintText(self, qp: QPainter):
        size = self.size()
        # draw text
        state_text = "EMPTY" if self._state == 0 else ("FULL" if self._state == 1 else "ANY")
        qp.setPen(QPen(QColor(0, 0, 0, 255), 1))
        qp.drawText(1, size.height() // 2, state_text)

    def _findPixmap(self) -> Optional[QPixmap]:
        if self._tile:
            return self._tile.pixmap()
        elif self._state != 0:
            return TileHandler.instance().getPixmap(1)
        return None

    def checkStateSet(self):
        return self._state

    def nextCheckState(self):
        self.setState(self._state + 1)

    def setTile(self, tile: "Tile"):
        self._tile = tile
        self.update()

    def setState(self, state):
        self._state = state
        self._state %= self._num_states  # Tri state button
        self.update()
