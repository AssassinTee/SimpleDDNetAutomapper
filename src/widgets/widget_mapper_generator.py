from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QRadioButton, QLabel, QPushButton, QFileDialog, \
    QMessageBox
from PyQt6.QtGui import QPixmap

from src.dialogs.dialog_check_map import CheckMapDialog


class MapperGeneratorWidget(QWidget):
    # noinspection PyUnresolvedReferences
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout()

        self.radio_layout = QHBoxLayout()
        self.radio_layout.addWidget(QRadioButton("Easy"))
        self.radio_layout.addWidget(QRadioButton("Normal"))
        self.radio_layout.addWidget(QRadioButton("Advanced"))
        self.layout.addLayout(self.radio_layout)

        self.image_label = QLabel("No Image")
        self.layout.addWidget(self.image_label)

        self.generate_button = QPushButton("Generate")
        self.generate_button.clicked.connect(self.open_file_dialog)
        self.layout.addWidget(self.generate_button)

        self.setLayout(self.layout)
        self.image_path = "data/img/grass_main.png"
        self.set_image(self.image_path)

    def set_image(self, image_path):
        pixmap = QPixmap(image_path)
        self.image_label.setPixmap(pixmap)
        self.image_path = image_path
        self.image_label.setScaledContents(True)
        self.image_label.setMaximumSize(200, 200)

    def open_file_dialog(self):
        cmd = CheckMapDialog(self)
        cmd.exec()
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
