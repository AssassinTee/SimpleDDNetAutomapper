from PyQt6.QtGui import QPainter, QPen, QColor, QPixmap, QImage
from PyQt6.QtCore import Qt

from src.backend.tile_modificators import TileMods
from src.backend.tile_status import TileStatus
from src.dialogs.dialog_tile_settings import TileSettingsDialog
from src.backend.tile_connection import TileConnection
from src.backend.tile_data import TileData
from src.backend.tile_handler import TileHandler
from src.config.app_state import AppState
from typing import Optional, Any

from src.widgets.widget_base_tile import BaseTile


class Tile(BaseTile):
    def __init__(self, tile_id: int, width=64, height=64) -> None:
        super().__init__(tile_id)
        self.setMaximumSize(width, height)
        self.hovered = False
        self.selected = False
        self.dialog = TileSettingsDialog(self)
        self.alpha = None
        self.setMouseTracking(True)
        self.lock = True  # lock as long as empty
        self.tile_checked: int = 0  # 0 = unchecked, 1 = configured, 2 = removed
        self.image: Optional[QImage] = None
        self.group_color: Optional[QColor] = None
        self.group_label: str = ""  # only the top left tile of a group is labelled
        self.group_chance: str = ""

    def paintEvent(self,
                   e: Any,
                   _: Any = None) -> None:
        # draw BaseTile
        super().paintEvent(e)

        # draw text
        if self.pixmap() or self.tile_id == 0:
            qp = QPainter(self)
            self.paintPixmapExists(qp)
            self.paintGroup(qp)
            qp.end()

    def setGroupOverlay(self, color: Optional[QColor], label: str = "", chance: str = "",
                        tooltip: str = ""):
        if color == self.group_color and label == self.group_label and chance == self.group_chance:
            return
        self.group_color = color
        self.group_label = label
        self.group_chance = chance
        self.setToolTip(tooltip)
        self.update()

    def paintGroup(self, qp: QPainter):
        if not self.group_color:
            return
        qp.fillRect(0, 0, self.width() - 1, self.height() - 1, self.group_color)
        qp.setPen(QPen(QColor(self.group_color.rgb()), 2))  # same color, but opaque
        qp.drawRect(0, 0, self.width() - 1, self.height() - 1)

        if self.group_label and self._drawOverlayText(qp, self.group_label, 1) and self.group_chance:
            self._drawOverlayText(qp, self.group_chance, 13)

    def _drawOverlayText(self, qp: QPainter, text: str, y: int) -> bool:
        # tiles get as small as the tileset allows, so only draw what still says something
        qp.setPen(QPen(QColor(255, 255, 255, 255), 1))
        available = self.width() - 4
        if y + 12 > self.height():
            return False
        elided = qp.fontMetrics().elidedText(text, Qt.TextElideMode.ElideRight, available)
        if qp.fontMetrics().horizontalAdvance(elided[:2]) > available:
            return False
        qp.drawText(2, y, available, 12, Qt.AlignmentFlag.AlignLeft, elided)
        return True

    def paintPixmapExists(self, qp: QPainter):
        if self.lock:
            # draw locked emoji
            qp.setPen(QPen(QColor(40, 40, 40, 255), 10))
            qp.drawText(self.width() - 20, self.height() - 20, 20, 20, Qt.AlignmentFlag.AlignVCenter, "🔒")
        else:
            if self.hovered or self.selected:
                qp.fillRect(0, 0, self.width() - 1, self.height() - 1, QColor(255, 255, 255, 100))

            if self.tile_data and self.tile_data.chance < 100:
                self._drawOverlayText(qp, f"{self.tile_data.chance:g}%", 1)

            if self.tile_data:
                if self.tile_checked == 0:
                    qp.setPen(QPen(QColor(255, 255, 0, 255), 10))
                    qp.drawText(self.width() - 20, self.height() - 20, 20, 20, Qt.AlignmentFlag.AlignVCenter, "?")
                elif self.tile_checked == 1:
                    qp.setPen(QPen(QColor(0, 255, 0, 255), 10))
                    qp.drawText(self.width() - 20, self.height() - 20, 20, 20, Qt.AlignmentFlag.AlignVCenter, "✔️")
                elif self.tile_checked == 2:
                    qp.setPen(QPen(QColor(255, 0, 0, 255), 10))
                    qp.drawText(self.width() - 20, self.height() - 20, 20, 20, Qt.AlignmentFlag.AlignVCenter, "❌")

        # draw outline
        pen = QPen(QColor(0, 0, 0, 127), 1)
        pen.setStyle(Qt.PenStyle.DotLine)
        qp.setPen(pen)
        qp.drawRect(0, 0, self.width() - 1, self.height() - 1)

    def mousePressEvent(self, event):
        if AppState.groupMode():
            clicker = self.parentWidget()
            if event.button() == Qt.MouseButton.RightButton:
                clicker.removeGroupAt(self.tile_id)
            else:
                clicker.groupDragStart(self.tile_id)
            return

        if event.button() == Qt.MouseButton.RightButton:
            self.rightMouseButtonClicked()
        else:
            self.leftMouseButtonClicked()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if AppState.groupMode():
            self.parentWidget().groupDragTo(event.globalPosition().toPoint())
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if AppState.groupMode():
            self.parentWidget().groupDragEnd()
            return
        super().mouseReleaseEvent(event)

    def leftMouseButtonClicked(self):
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
            self.dialog.setTileData(self.tile_data)
        ret = self.dialog.exec()
        # ok pressed
        if ret == 1:
            # update tile data in handler
            self.tile_data = self.dialog.getTileData()
            self.tile_checked = 1
            TileHandler.instance().updateTileStorage(self)

        # mark tile as deselected after dialog
        self.selected = False
        self.update()

    def rightMouseButtonClicked(self):
        if self.lock:
            return

        TileHandler.instance().removeTileFromStorage(self.tile_id)
        self.tile_checked = 2
        self.update()

    def enterEvent(self, event):
        self.hovered = True
        self.update()

    def leaveEvent(self, event):
        self.hovered = False
        self.update()

    def setPixmap(self, pixmap: QPixmap):
        super().setPixmap(pixmap)
        TileHandler.instance().addPixmap(self)
        self.image = pixmap.toImage().convertToFormat(QImage.Format.Format_ARGB32)
        self.scanImage()

    def scanImage(self):
        self._scanImageAnyAlpha()
        if not self.lock:
            self._scanCornersAndEdges()

    def _scanImageAnyAlpha(self):
        if not self.image:
            return
        img = self.image.convertToFormat(QImage.Format.Format_ARGB32)
        bpl = img.bytesPerLine()
        width = img.width()
        buf = img.constBits().asarray(bpl * img.height())
        # Format_ARGB32 in memory (little-endian) is B,G,R,A per pixel, so alpha is byte index 3
        for y in range(img.height()):
            row_start = y * bpl
            for x in range(width):
                if buf[row_start + x * 4 + 3] != 0:
                    self.lock = False
                    return

    def _scanCornersAndEdges(self):
        has_alpha_neighbors = []
        empty = False
        width = self.image.width()
        height = self.image.height()
        for yi, y in enumerate([0, height // 2, height - 1]):
            for xi, x in enumerate([0, width // 2, width - 1]):
                val = self.image.pixel(x, y)  # here it's okay, because I just check 8 values
                alpha = (val & 0xFF000000) >> 24
                if yi == 1 and xi == 1:  # scan the middle
                    empty = alpha == 0
                else:
                    has_alpha_neighbors.append(int(alpha > 0))

        # todo autodetect symmetry for flip and rot
        ts = TileStatus()
        ts.empty = empty
        tc = TileConnection(has_alpha_neighbors)
        tm = TileMods(False, False, False)
        self.tile_data = TileData(tc, ts, tm)
        # don't save them in the handler, only solve valid tiles there
        # TileHandler.instance().updateTileRelations(self)
