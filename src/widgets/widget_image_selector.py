from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QFileDialog
from PyQt6.QtGui import QPixmap

from src.config.app_state import AppState
from src.widgets.widget_tile_clicker import TileClicker


class ImageSelectorWidget(QWidget):
    # noinspection PyUnresolvedReferences
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Image Selector")
        self.setGeometry(100, 100, 400, 300)

        self.image_label = TileClicker(self)
        # self.image_label.setScaledContents(True)
        # self.image_label.setMaximumSize(1024,1024)

        self.select_button = QPushButton("Select Image")
        self.select_button.clicked.connect(self.select_image)
        self.select_button.setMaximumWidth(1024)

        layout = QVBoxLayout()
        layout.addWidget(self.select_button)
        layout.addWidget(self.image_label)
        self.setLayout(layout)

    def select_image(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.bmp)")
        file_dialog.setViewMode(QFileDialog.ViewMode.List)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)

        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                image_path = selected_files[0]
                pixmap = QPixmap(image_path)
                if AppState.imagePath():
                    AppState.reset()  # reset app before loading new, calls self.reset somewhere
                if not pixmap.isNull():
                    self.image_label.setPixmap(pixmap)
                    AppState.setImagePath(image_path)
                # else:
                #    self.image_label.setText("Invalid image file")

    def reset(self):
        self.layout().removeWidget(self.image_label)
        self.image_label = TileClicker(self)
        self.layout().addWidget(self.image_label)
