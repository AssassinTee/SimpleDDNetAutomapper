from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QFileDialog
from PyQt5.QtGui import QPixmap
from widgets.widget_tile_clicker import TileClicker

class ImageSelectorWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Image Selector")
        self.setGeometry(100, 100, 400, 300)

        self.image_label = TileClicker()
        #self.image_label.setScaledContents(True)
        #self.image_label.setMaximumSize(1024,1024)

        self.select_button = QPushButton("Select Image")
        self.select_button.clicked.connect(self.select_image)
        self.select_button.setMaximumWidth(1024)

        layout = QVBoxLayout()
        layout.addWidget(self.select_button)
        layout.addWidget(self.image_label)
        self.setLayout(layout)

    def select_image(self):
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.bmp)")
        file_dialog.setViewMode(QFileDialog.List)
        file_dialog.setFileMode(QFileDialog.ExistingFile)

        if file_dialog.exec_():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                image_path = selected_files[0]
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    self.image_label.setPixmap(pixmap)
                else:
                    self.image_label.setText("Invalid image file")