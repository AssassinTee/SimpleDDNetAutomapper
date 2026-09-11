from pathlib import Path

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

    def tileClicker(self) -> TileClicker:
        return self.image_label

    def select_image(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.bmp)")
        file_dialog.setViewMode(QFileDialog.ViewMode.List)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)

        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                self.loadImage(Path(selected_files[0]))

    def loadImage(self, image_path: Path) -> bool:
        pixmap = QPixmap(str(image_path))
        if pixmap.isNull():
            return False
        if AppState.imagePath():
            AppState.reset()  # reset app before loading new, calls self.reset somewhere
        self.image_label.setPixmap(pixmap)
        AppState.setImagePath(image_path)
        return True

    def reset(self):
        old = self.image_label
        self.layout().removeWidget(old)
        old.deleteLater()
        self.image_label = TileClicker(self)
        self.layout().addWidget(self.image_label)
