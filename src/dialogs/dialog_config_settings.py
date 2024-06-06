import os
from pathlib import Path

from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QGridLayout, QLabel, QFileDialog, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QDialogButtonBox

from src.config.config_manager import ConfigManager


class ConfigSettingsDialog(QDialog):
    def __init__(self, *args):
        super().__init__(*args)
        self.setWindowTitle("Settings")
        self.layout: QGridLayout = QGridLayout()

        configs = [
            ("client_path", "Client path:", QFileDialog.FileMode.ExistingFile),
            ("data_path", "Data directory path:", QFileDialog.FileMode.Directory)
        ]

        index = 0
        for index, (config, label, filemode) in enumerate(configs):
            client_path = ConfigManager.config()[config]
            config_button = QPushButton(client_path, parent=self)
            q_label = QLabel(label)
            self.layout.addWidget(q_label, index, 0)
            self.layout.addWidget(config_button, index, 1)
            handler = self.createBrowseSettingHandler(config, q_label.text(), config_button, filemode)
            config_button.clicked.connect(handler)

        q_btn = QDialogButtonBox.StandardButton.Ok

        self.buttonBox = QDialogButtonBox(q_btn)
        self.buttonBox.accepted.connect(self.accept)
        self.layout.addWidget(self.buttonBox, index + 1, 0, 1, 2, Qt.AlignmentFlag.AlignHCenter)
        self.setLayout(self.layout)

        self.setModal(True)

    def createBrowseSettingHandler(self, setting: str, text: str, config_button: QPushButton,
                                   filemode: QFileDialog.FileMode):
        def handler():
            self.browseSetting(setting, text, config_button, filemode)
        return handler

    def browseSetting(self, setting: str, text: str, config_button: QPushButton, filemode: QFileDialog.FileMode):
        value = ConfigManager.config()[setting]
        if not value:
            directory = os.getcwd()
        else:
            directory = Path(value).parent if Path(value).is_file() else (
                value if Path(value).is_dir() else os.getcwd())

        dialog = QFileDialog(self, caption=text)
        dialog.setFileMode(filemode)
        dialog.setDirectory(str(directory))
        if dialog.exec():
            paths = dialog.selectedFiles()
            if paths:
                path = paths[0]
                ConfigManager.setConfig(setting, path)
                config_button.setText(path)
