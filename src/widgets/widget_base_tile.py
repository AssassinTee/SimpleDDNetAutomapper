from typing import Any, Optional

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QPainter, QTransform, QPixmap
from PyQt6.QtWidgets import QLabel, QSizePolicy, QApplication

from src.images_helper import ImageHelper
from src.backend.tile_data import TileData


class BaseTile(QLabel):
    def __init__(self, tile_id: int, tile_data: Optional[TileData] = None, fixed_size: Optional[int] = None, *__args):
        super().__init__(*__args)
        self.tile_data = tile_data
        self.tile_id = tile_id

        if fixed_size:
            self.setFixedSize(QSize(fixed_size, fixed_size))

    def getID(self) -> int:
        return self.tile_id

    def paintEvent(self, e: Any, _: Any = None) -> None:
        qp = QPainter(self)

        # draw background
        ImageHelper.instance().drawCheckerImage(qp, self.size().width(), self.size().height())

        pm: Optional[QPixmap] = self.pixmap()
        if pm and pm.width() > 0 and pm.height() > 0:
            # handle transformations
            transform = QTransform()

            if self.width() != pm.width() or self.height() != pm.height():
                factor_width = self.width() / pm.width()
                factor_height = self.height() / pm.height()
                transform.scale(factor_width, factor_height)

            if self.tile_data:
                transform.translate(pm.width() // 2, pm.height() // 2)
                if self.tile_data.status.h_flip:
                    transform = transform.scale(1, -1)

                if self.tile_data.status.v_flip:
                    transform = transform.scale(-1, 1)

                if self.tile_data.status.rot:
                    transform.rotate(self.tile_data.status.rot)
                transform.translate(-pm.width() // 2, -pm.height() // 2)

            # draw tile
            qp.setTransform(transform)
            qp.drawPixmap(0, 0, pm)

            # qp.drawText(self, 0, pm.height() // 2, )

        qp.end()

    def __copy__(self):
        tile_data = None
        if self.tile_data:
            tile_data = self.tile_data.__copy__()
        cp = BaseTile(self.tile_id, tile_data)
        if self.pixmap():
            cp.setPixmap(self.pixmap())
        return cp
