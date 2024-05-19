from PyQt6.QtGui import QPainter, QPen, QColor, QPixmap, QImage
from PyQt6.QtCore import Qt

from logic.tile_modificators import TileMods
from src.logic.tile_status import TileStatus
from src.dialogs.dialog_tile_settings import TileSettingsDialog
from src.logic.tile_connection import TileConnection
from src.logic.tile_data import TileData
from src.logic.tile_handler import TileHandler
from typing import Optional, Any

from widgets.widget_base_tile import BaseTile


class Tile(BaseTile):
    def __init__(self, tile_id: int, width=64, height=64) -> None:
        super().__init__(tile_id)
        self.width = width
        self.height = height
        self.setMaximumSize(width, height)

        self.mousePressEvent = self.openDialog
        self.hovered = False
        self.selected = False
        self.dialog = TileSettingsDialog(self)
        self.alpha = None
        self.setMouseTracking(True)
        self.lock = True  # lock as long as empty
        self.data_checked = False  # true after checked
        self.image: Optional[QImage] = None

    def paintEvent(self,
                   e: Any,
                   _: Any = None) -> None:
        # draw BaseTile
        super().paintEvent(e)

        # draw text
        if self.pixmap() or self.tile_id == 0:
            qp = QPainter(self)
            self.paintPixmapExists(qp)
            qp.end()

    def paintPixmapExists(self, qp: QPainter):
        if self.lock:
            # draw locked emoji
            qp.setPen(QPen(QColor(40, 40, 40, 255), 10))
            qp.drawText(self.width - 20, self.height - 20, 20, 20, Qt.AlignmentFlag.AlignVCenter, "🔒")
        else:
            if self.hovered or self.selected:
                qp.fillRect(0, 0, self.width - 1, self.height - 1, QColor(255, 255, 255, 100))

            if self.tile_data:
                if self.data_checked:
                    qp.setPen(QPen(QColor(0, 255, 0, 255), 10))
                    qp.drawText(self.width - 20, self.height - 20, 20, 20, Qt.AlignmentFlag.AlignVCenter, "✔️")
                else:
                    qp.setPen(QPen(QColor(255, 255, 0, 255), 10))
                    qp.drawText(self.width - 20, self.height - 20, 20, 20, Qt.AlignmentFlag.AlignVCenter, "?")

        # draw outline
        pen = QPen(QColor(0, 0, 0, 127), 1)
        pen.setStyle(Qt.PenStyle.DotLine)
        qp.setPen(pen)
        qp.drawRect(0, 0, self.width - 1, self.height - 1)

    def openDialog(self, _):
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
            print(self.tile_data.con)
            self.data_checked = True
            TileHandler.instance().updateTileStorage(self)

        # mark tile as deselected after dialog
        self.selected = False
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
        for y in range(self.image.height()):
            for x in range(self.image.width()):
                val = self.image.pixel(x, y)  # this is fucking inefficient, but nothing else worked
                alpha = (val & 0xFF000000) >> 24
                if alpha > 0:
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
