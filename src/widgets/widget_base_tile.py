from typing import Any

from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QLabel

from images_helper import ImageHelper


class BaseTile(QLabel):
    def __init__(self, *__args):
        super().__init__(*__args)

    def paintEvent(self, e: Any, _: Any = None) -> None:
        qp = QPainter(self)

        # draw background
        ImageHelper.instance().drawCheckerImage(qp, self.size().width(), self.size().height())
        qp.end()
        super().paintEvent(e)
