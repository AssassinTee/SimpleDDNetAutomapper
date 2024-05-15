from typing import TYPE_CHECKING

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtWidgets import QGridLayout, QCheckBox

from buttons.button_tile_connection import TileConnectionButton

if TYPE_CHECKING:
    from src.widgets.widget_tile import Tile


class TileConnectionCenterButton(TileConnectionButton):
    def __init__(self, tile: "Tile", parent=None):
        super().__init__(parent)
        self._tile = tile
        self._main = True
        self._state = 1  # full, default state
        self._num_states = 2  # this tile can only be full or empty
        layout = QGridLayout()
        checkbox_contents = [
            ["V-Flip", "Allow center tile to be flipped vertically"],
            ["H-Flip", "Allow center tile to be flipped horizontally"],
            ["Rotate", "Allow center tile to be rotated"],
            ["Empty", "Allow center tile to be placed on empty blocks"],
        ]
        for i, (name, tool_tip) in enumerate(checkbox_contents):
            widget = QCheckBox(name)
            widget.setToolTip(tool_tip)
            layout.addWidget(widget, i // 2, i % 2)

        self.setLayout(layout)

    # override
    def _paintOutline(self, qp: QPainter):
        size = self.size()
        pen = QPen(QColor(0, 0, 0, 255), 1)
        pen.setStyle(Qt.DotLine)
        qp.setPen(pen)
        qp.drawRect(0, 0, size.width() - 1, size.height() - 1)
        pen.setStyle(Qt.SolidLine)
        qp.setPen(pen)

    # override
    def _paintText(self, qp: QPainter):
        pass

    def setTile(self, tile: "Tile"):
        # TODO set checkboxes
        self._tile = tile
        self.update()
