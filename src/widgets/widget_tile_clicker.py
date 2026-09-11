from typing import NamedTuple, Optional, Tuple

from PyQt6.QtCore import QPoint
from PyQt6.QtGui import QColor, QPixmap
from PyQt6.QtWidgets import QWidget, QGridLayout

from src.backend.group_handler import GroupHandler
from src.backend.tile_group import TileGroup
from src.config.app_state import AppState
from src.dialogs.dialog_group_settings import configureGroup
from src.globals import TILESET_COL, TILESET_ROW, NUM_TILES
from src.signals.signal_emitter import ApplicationStatusEnum
from src.widgets.widget_tile import Tile

GOLDEN_ANGLE = 137.5  # consecutive hues land as far apart on the circle as they can
DRAG_COLOR = QColor(255, 255, 255, 130)


def groupColor(index: int) -> QColor:
    # pastel and half transparent, the tileset underneath still has to be readable
    return QColor.fromHslF(index * GOLDEN_ANGLE % 360 / 360, 0.6, 0.72, 110 / 255)


class GroupOverlay(NamedTuple):
    color: Optional[QColor] = None
    label: str = ""
    chance: str = ""
    tooltip: str = ""


class TileClicker(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.gridLayout = QGridLayout()
        self.gridLayout.setHorizontalSpacing(0)
        self.gridLayout.setVerticalSpacing(0)
        self.setLayout(self.gridLayout)
        self.tiles = []
        self.drag_anchor: Optional[int] = None
        self.drag_corner: Optional[int] = None
        self.pending_edit: Optional[TileGroup] = None

    def setPixmap(self, pixmap: QPixmap):
        tile_width = pixmap.width() // TILESET_COL
        tile_height = pixmap.height() // TILESET_ROW
        tile_width_float = pixmap.width() / TILESET_COL
        tile_height_float = pixmap.height() / TILESET_ROW

        self.tiles = []

        for i in range(NUM_TILES):
            row = i // TILESET_COL
            col = i % TILESET_COL
            tile_widget = Tile(i, width=tile_width, height=tile_height)
            self.tiles.append(tile_widget)
            self.gridLayout.addWidget(tile_widget, row + 1, col + 1)

        # handle all tiles except 0, handle tile 0 separately
        for i in range(1, NUM_TILES):
            tile = self.tiles[i]

            # yes, there might be gaps due to bad tilesets
            x = int((i % TILESET_COL) * tile_width_float)
            y = int((i // TILESET_ROW) * tile_height_float)
            tile.setPixmap(pixmap.copy(x, y, tile_width, tile_height))

        self.gridLayout.setRowStretch(0, 1)
        self.gridLayout.setColumnStretch(0, 1)
        self.gridLayout.setRowStretch(TILESET_ROW + 1, 1)
        self.gridLayout.setColumnStretch(TILESET_COL + 1, 1)
        self.refreshGroups()

    def groupDragStart(self, tile_id: int):
        # a press inside an existing group means "configure that one", the same as clicking a tile
        self.pending_edit = GroupHandler.instance().groupAt(tile_id)
        if self.pending_edit:
            return
        self.drag_anchor = tile_id
        self.drag_corner = tile_id
        self.refreshGroups()

    def groupDragTo(self, global_pos: QPoint):
        if self.drag_anchor is None:
            return
        # during a drag Qt keeps delivering to the tile that got the press, so find the one under the cursor
        tile = self.tileAt(global_pos)
        if tile is None or tile.tile_id == self.drag_corner:
            return
        self.drag_corner = tile.tile_id
        self.refreshGroups()

    def groupDragEnd(self):
        if self.pending_edit is not None:
            group, self.pending_edit = self.pending_edit, None
            configureGroup(group, self)
            return
        if self.drag_anchor is None:
            return
        top_left, width, height = self._dragRect()
        self.drag_anchor = None
        self.drag_corner = None

        try:
            GroupHandler.instance().addGroup(top_left, width, height)
        except ValueError as e:
            AppState.setStatus(ApplicationStatusEnum.WARNING, str(e))
            self.refreshGroups()
            return
        AppState.groupsChanged()

    def removeGroupAt(self, tile_id: int):
        group = GroupHandler.instance().groupAt(tile_id)
        if not group:
            return
        GroupHandler.instance().removeGroup(group.name)
        AppState.groupsChanged()

    def tileAt(self, global_pos: QPoint) -> Optional[Tile]:
        child = self.childAt(self.mapFromGlobal(global_pos))
        while child is not None and not isinstance(child, Tile):
            child = child.parentWidget()
        return child

    def refreshGroups(self):
        overlay = {}
        for i, group in enumerate(GroupHandler.instance().getGroups()):
            color = groupColor(i)
            tooltip = (f"{group.name} — {group.width}x{group.height}, "
                       f"{group.mode.value}, {group.chance:g}%")
            for tile_id in group.tileIds():
                overlay[tile_id] = GroupOverlay(color, tooltip=tooltip)
            # only the corner is labelled, the rest of the footprint is too small for text
            chance = "" if group.chance >= 100 else f"{group.chance:g}%"
            overlay[group.top_left] = GroupOverlay(color, group.name, chance, tooltip)

        if self.drag_anchor is not None:
            top_left, width, height = self._dragRect()
            for y in range(height):
                for x in range(width):
                    overlay[top_left + y * TILESET_COL + x] = GroupOverlay(DRAG_COLOR)

        for tile in self.tiles:
            tile.setGroupOverlay(*overlay.get(tile.tile_id, GroupOverlay()))

    def _dragRect(self) -> Tuple[int, int, int]:
        rows = sorted([self.drag_anchor // TILESET_COL, self.drag_corner // TILESET_COL])
        cols = sorted([self.drag_anchor % TILESET_COL, self.drag_corner % TILESET_COL])
        top_left = rows[0] * TILESET_COL + cols[0]
        return top_left, cols[1] - cols[0] + 1, rows[1] - rows[0] + 1
