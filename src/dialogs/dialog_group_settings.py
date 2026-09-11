from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QComboBox,
                             QSpinBox, QDialogButtonBox)

from src.backend.group_handler import GroupHandler
from src.backend.tile_group import GroupMode, TileGroup
from src.config.app_state import AppState
from src.signals.signal_emitter import ApplicationStatusEnum

MODE_HINTS = {
    GroupMode.FILL: "Packs into solid areas. Only the group itself has to be solid.",
    GroupMode.DECORATE: "Sits deep inside solid areas. The ring around the group has to be solid too.",
}


class GroupSettingsDialog(QDialog):
    def __init__(self, group: TileGroup, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configure Group")

        self.name_edit = QLineEdit(group.name)
        self.mode_combobox = QComboBox()
        for mode in GroupMode:
            self.mode_combobox.addItem(mode.value.capitalize(), mode)
        self.mode_combobox.setCurrentIndex(self.mode_combobox.findData(group.mode))
        self.chance_spinbox = QSpinBox()
        self.chance_spinbox.setRange(1, 100)
        self.chance_spinbox.setSuffix(" %")
        self.chance_spinbox.setValue(int(group.chance))

        form = QFormLayout()
        form.addRow("Name:", self.name_edit)
        form.addRow("Mode:", self.mode_combobox)
        form.addRow("Chance:", self.chance_spinbox)

        self.mode_hint_label = QLabel()
        self.mode_hint_label.setWordWrap(True)
        self.mode_hint_label.setEnabled(False)

        size_label = QLabel(f"Tile {group.top_left}, {group.width}x{group.height}")
        size_label.setEnabled(False)

        standard_buttons = QDialogButtonBox.StandardButton
        buttons = QDialogButtonBox(standard_buttons.Ok | standard_buttons.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(size_label)
        layout.addLayout(form)
        layout.addWidget(self.mode_hint_label)
        layout.addWidget(buttons)
        self.setLayout(layout)

        self.mode_combobox.currentIndexChanged.connect(self.updateModeHint)
        self.updateModeHint()
        self.setModal(True)

    def updateModeHint(self):
        self.mode_hint_label.setText(MODE_HINTS[self.mode_combobox.currentData()])


def configureGroup(group: TileGroup, parent=None):
    dialog = GroupSettingsDialog(group, parent)
    if dialog.exec() != 1:
        return

    group.mode = dialog.mode_combobox.currentData()
    group.chance = float(dialog.chance_spinbox.value())
    try:
        GroupHandler.instance().renameGroup(group.name, dialog.name_edit.text())
    except ValueError as e:
        AppState.setStatus(ApplicationStatusEnum.WARNING, str(e))
    AppState.groupsChanged()
