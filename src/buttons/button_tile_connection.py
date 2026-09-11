from typing import TYPE_CHECKING, Any, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QPixmap, QColor, QPen, QTransform
from PyQt6.QtWidgets import QAbstractButton

from src.images_helper import ImageHelper
from src.backend.tile_handler import TileHandler
from src.backend.tile_status import TileStatus
from src.signals.signal_emitter import ConfigurationClickedEmitter

if TYPE_CHECKING:
    from src.widgets.widget_tile import Tile


class TileConnectionButton(QAbstractButton):
    """
    dir: orientation to the next connection, 0 is up, 2 is right (clockwise)
    """

    hover_width = 2

    def __init__(self, button_id, parent=None):
        super().__init__(parent)
        self.signal_emitter = ConfigurationClickedEmitter(parent)
        self.button_id = button_id
        self._state = 2  # Any
        self._num_states = 3
        self._tile = None
        self._tile_status = None
        self._main = False
        self.setMinimumSize(128, 128)
        self.setMaximumSize(128, 128)

    def paintEvent(self, _e: Any, _qpe: Any = None) -> None:
        qp = QPainter(self)

        # draw background
        if self._state != 2:
            ImageHelper.instance().drawCheckerImage(qp, self.size().width(), self.size().height())

        self._paintTile(qp)
        self._paintOutline(qp)
        self._paintHover(qp)
        self._paintText(qp)
        qp.end()

    def _paintTile(self, qp: QPainter):
        if self._state == 2:
            return
        size = self.size()

        # draw tile
        pm = self._findPixmap()
        if pm:
            transform = QTransform()

            if size.width() != pm.width() or size.height() != pm.height():
                factor_width = size.width() / pm.width()
                factor_height = size.height() / pm.height()
                transform.scale(factor_width, factor_height)

            if self._tile_status:
                transform.translate(pm.width() // 2, pm.height() // 2)

                # rotate first, because otherwise you might rotate your flip breaking this in the process
                if self._tile_status.rot:
                    transform.rotate(90)

                if self._tile_status.y_flip:
                    transform = transform.scale(1, -1)

                if self._tile_status.x_flip:
                    transform = transform.scale(-1, 1)

                transform.translate(-pm.width() // 2, -pm.height() // 2)

            qp.setTransform(transform)
            qp.drawPixmap(0, 0, pm)
            qp.resetTransform()

    # will be overwritten
    def _paintOutline(self, qp: QPainter):
        return

    def _paintHover(self, qp: QPainter):
        if not self.underMouse():
            return
        size = self.size()
        qp.setPen(QPen(QColor(255, 190, 0, 255), self.hover_width))
        inset = self.hover_width // 2
        qp.drawRect(inset, inset,
                    size.width() - self.hover_width,
                    size.height() - self.hover_width)

    def _paintText(self, qp: QPainter):
        # draw text
        state_text = "EMPTY" if self._state == 0 else ("FULL" if self._state == 1 else "ANY")
        qp.setPen(QPen(QColor(0, 0, 0, 255), 1))
        qp.drawText(self.rect(), int(Qt.AlignmentFlag.AlignCenter), state_text)

    def _findPixmap(self) -> Optional[QPixmap]:
        if self._state != 0:
            if self._tile:
                return self._tile.pixmap()
            return TileHandler.instance().getPixmap(1)
        return None

    def checkStateSet(self) -> int:
        return self._state

    def nextCheckState(self):
        self.setState(self._state + 1)

    def previousCheckState(self):
        self.setState(self._state - 1)

    def mouseReleaseEvent(self, e):
        if not self.hitButton(e.position().toPoint()):
            return  # cursor left the button, cancel
        match e.button():
            case Qt.MouseButton.LeftButton:
                self.nextCheckState()
            case Qt.MouseButton.RightButton:
                self.previousCheckState()

    def enterEvent(self, e):
        self.update()
        super().enterEvent(e)

    def leaveEvent(self, e):
        self.update()
        super().leaveEvent(e)

    def setTile(self, tile: Optional["Tile"], update_neighbors=True, tile_status: Optional[TileStatus] = None):
        if self._tile and tile:
            same_id = self._tile.getID() == tile.getID()
            same_status = self._tile_status is not None and tile_status is not None \
                and self._tile_status == tile_status
            if same_id and same_status:
                return

        if tile is None:
            self._tile = tile
            self._tile_status = None
        else:
            self._tile = tile.__copy__()
            self._tile_status = tile_status.__copy__() if tile_status else None

        if update_neighbors:
            self._update_neighborhood()
        self.update()

    def setState(self, state):
        if self._state != state:
            self._state = state
            self._state %= self._num_states  # Tri state button
            self._update_neighborhood()
            self.update()

    def _update_neighborhood(self):
        self.signal_emitter.neighbor_signal.emit(self.button_id)
