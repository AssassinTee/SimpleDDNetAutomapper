from typing import Optional

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QCheckBox, QLabel, QListWidget,
                             QListWidgetItem, QPushButton)

from src.backend.group_handler import GroupHandler
from src.backend.tile_group import TileGroup
from src.config.app_state import AppState
from src.dialogs.dialog_group_settings import configureGroup

HINT = ("Drag across the tileset to define a rectangular group.\n"
        "Click a group to configure it, right-click to remove it.")

ORDER_HINT = "Groups are placed top to bottom, and whoever comes first gets first pick."


class GroupEditorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.group_mode_checkbox = QCheckBox("Define groups (drag on the tileset)")
        self.hint_label = QLabel(HINT)
        self.hint_label.setWordWrap(True)
        self.hint_label.setEnabled(False)

        self.group_list = QListWidget()

        self.up_button = QPushButton("▲")
        self.down_button = QPushButton("▼")
        for button in (self.up_button, self.down_button):
            button.setMaximumWidth(32)
        self.up_button.setToolTip("Place this group before the one above it")
        self.down_button.setToolTip("Place this group after the one below it")

        list_row = QHBoxLayout()
        list_row.addWidget(self.group_list)
        order_column = QVBoxLayout()
        order_column.addWidget(self.up_button)
        order_column.addWidget(self.down_button)
        order_column.addStretch(1)
        list_row.addLayout(order_column)

        self.order_hint_label = QLabel(ORDER_HINT)
        self.order_hint_label.setWordWrap(True)
        self.order_hint_label.setEnabled(False)

        self.edit_button = QPushButton("Configure group")
        self.remove_button = QPushButton("Remove group")

        layout = QVBoxLayout()
        layout.addWidget(self.group_mode_checkbox)
        layout.addWidget(self.hint_label)
        layout.addLayout(list_row)
        layout.addWidget(self.order_hint_label)
        layout.addWidget(self.edit_button)
        layout.addWidget(self.remove_button)
        self.setLayout(layout)

        self.group_mode_checkbox.toggled.connect(self.groupModeToggled)
        self.group_list.currentItemChanged.connect(self.updateButtons)
        self.group_list.itemDoubleClicked.connect(self.editSelected)
        self.up_button.clicked.connect(lambda: self.moveSelected(-1))
        self.down_button.clicked.connect(lambda: self.moveSelected(1))
        self.edit_button.clicked.connect(self.editSelected)
        self.remove_button.clicked.connect(self.removeSelected)

        self.refresh()

    def groupModeToggled(self, enabled: bool):
        AppState.setGroupMode(enabled)
        self.hint_label.setEnabled(enabled)

    def selectedGroup(self) -> Optional[TileGroup]:
        item = self.group_list.currentItem()
        if not item:
            return None
        return GroupHandler.instance().groups.get(item.data(1))

    def refresh(self):
        selected = self.group_list.currentItem()
        selected_name = selected.data(1) if selected else None

        self.group_list.clear()
        for group in GroupHandler.instance().getGroups():
            chance = "" if group.chance >= 100 else f", {group.chance:g}%"
            item = QListWidgetItem(f"{group.name}  —  {group.width}x{group.height}, "
                                   f"{group.mode.value}{chance}")
            item.setData(1, group.name)
            self.group_list.addItem(item)
            if group.name == selected_name:
                self.group_list.setCurrentItem(item)

        if self.group_list.currentItem() is None and self.group_list.count():
            self.group_list.setCurrentRow(self.group_list.count() - 1)

        self.updateButtons()

    def updateButtons(self):
        row = self.group_list.currentRow()
        has_group = self.selectedGroup() is not None
        for button in (self.edit_button, self.remove_button):
            button.setEnabled(has_group)
        self.up_button.setEnabled(has_group and row > 0)
        self.down_button.setEnabled(has_group and row < self.group_list.count() - 1)

    def moveSelected(self, offset: int):
        group = self.selectedGroup()
        if group and GroupHandler.instance().moveGroup(group.name, offset):
            AppState.groupsChanged()

    def editSelected(self):
        group = self.selectedGroup()
        if group:
            configureGroup(group, self)

    def removeSelected(self):
        group = self.selectedGroup()
        if not group:
            return
        GroupHandler.instance().removeGroup(group.name)
        AppState.groupsChanged()

    def reset(self):
        self.group_mode_checkbox.setChecked(False)
        self.refresh()
