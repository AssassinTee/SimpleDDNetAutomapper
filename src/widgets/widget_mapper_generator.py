import subprocess
from pathlib import Path

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QRadioButton, QLabel, QPushButton, QLineEdit, QComboBox
from PyQt6.QtGui import QPixmap, QRegularExpressionValidator
from PyQt6.QtCore import QRegularExpression

from src.config.app_state import AppState
from src.dialogs.dialog_check_map import CheckMapDialog
from src.config.config_manager import ConfigManager


class MapperGeneratorWidget(QWidget):
    # noinspection PyUnresolvedReferences
    def __init__(self, parent=None):
        super().__init__(parent)

        # vertical list
        self.layout = QVBoxLayout()

        # add radio buttons
        self.radio_layout = QHBoxLayout()
        radio_button_labels = ["New", "Overwrite existing"]
        self.radio_buttons = [QRadioButton(label) for label in radio_button_labels]
        for radio_button in self.radio_buttons:
            self.radio_layout.addWidget(radio_button)
        # select first radio button
        self.radio_buttons[0].setChecked(True)
        self.layout.addLayout(self.radio_layout)

        # new automapper
        self.new_mapper = QWidget()
        new_mapper_layout = QHBoxLayout()
        self.new_mapper_line_edit = QLineEdit()
        new_mapper_layout.addWidget(QLabel("Name Mapping Rule:"))
        new_mapper_layout.addWidget(self.new_mapper_line_edit)
        self.new_mapper.setLayout(new_mapper_layout)
        self.layout.addWidget(self.new_mapper)

        # existing auto mapper
        self.existing_mapper = QWidget()
        existing_mapper_layout = QHBoxLayout()
        self.existing_mapper_combobox = QComboBox()
        self.existing_mapper_combobox.insertItem(0, "TODO")
        existing_mapper_layout.addWidget(QLabel("Select Mapping Rule:"))
        existing_mapper_layout.addWidget(self.existing_mapper_combobox)
        self.existing_mapper.setLayout(existing_mapper_layout)
        self.layout.addWidget(self.existing_mapper)
        # hide by default
        self.existing_mapper.hide()
        # self.select_auto_mapper = QSelect()

        # Placeholder
        self.image_label = QLabel("No Image")
        self.layout.addWidget(self.image_label)

        # check ddnet
        self.ddnet_push_button = QPushButton("Check with ddnet")
        self.layout.addWidget(self.ddnet_push_button)
        if ConfigManager.instance().config()["client_path"] is None:
            self.ddnet_push_button.setDisabled(True)

        # spacer
        self.layout.addStretch(1)

        # Generate button
        self.generate_button = QPushButton("Generate")
        self.layout.addWidget(self.generate_button)

        self.setLayout(self.layout)
        self.image_path = "data/img/grass_main.png"
        self.setImage(self.image_path)

        # handle connections
        for radio_button in self.radio_buttons:
            radio_button.toggled.connect(self.ruleNameToggle)
        self.generate_button.clicked.connect(self.openFileDialog)
        self.ddnet_push_button.clicked.connect(self.startDDNetCheck)

        # some configuration
        # configure validator new_mapper_line_edit
        # this may break entering utf16 characters. Won't fix until somebody breaks it
        pattern = QRegularExpression(r'^[\w\d-]+$')  # disallow whitespaces and other special characters
        validator = QRegularExpressionValidator(pattern, self)
        self.new_mapper_line_edit.setValidator(validator)

        # https://github.com/ddnet/ddnet/blob/c7dc7b6a94528040678b7a0fab17ccb447e1d94d/src/game/editor/auto_map.h#L52
        self.new_mapper_line_edit.setMaxLength(128)  # limit number of characters

    def setImage(self, image_path):
        pixmap = QPixmap(image_path)
        self.image_label.setPixmap(pixmap)
        self.image_path = image_path
        self.image_label.setScaledContents(True)
        self.image_label.setMaximumSize(200, 200)

    def openFileDialog(self):
        rule_name = self.new_mapper_line_edit.text()
        if not AppState.imagePath() or not len(rule_name):
            return
        cmd = CheckMapDialog(self)
        ret = cmd.exec()
        if ret:
            loaded_image_path = Path(AppState.imagePath())
            filename = f"{loaded_image_path.stem}.rules"
            AppState.ruleManager().saveRule(filename, rule_name)
        """
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "All Files (*);;Text Files (*.txt)",
                                                   options=options)
        if file_path:
            if self.image_path:
                # Save the image to the specified file path
                QMessageBox.information(self, "Success", "Image and file saved successfully!")
            else:
                QMessageBox.warning(self, "Warning", "Please select an image first.")
        """

    def ruleNameToggle(self):
        if self.radio_buttons[0].isChecked():
            self.existing_mapper.hide()
            self.new_mapper.show()
        elif self.radio_buttons[1].isChecked():
            self.new_mapper.hide()
            self.existing_mapper.show()

    def startDDNetCheck(self):
        # TODO
        # generate Map
        # add tmp mapping rule
        # automap map with debroijn torus
        # open map with ddnet
        map_name = ""
        client_path = ConfigManager.instance().config()["client_path"]
        if not client_path:
            self.ddnet_push_button.setDisabled(True)
            return
        cmd = [client_path, map_name]
        subprocess.Popen(cmd, start_new_session=True)
