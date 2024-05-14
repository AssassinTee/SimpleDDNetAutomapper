import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QFileDialog, QHBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

from widgets.widget_image_selector import ImageSelectorWidget
from dockwidgets.dockwidget_mapper_generator import MapperGeneratorDockwidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple DDNet Automapper")
        self.resize(800, 600)  # Set initial size if needed
        self.setMaximumSize(1920, 1080)  # Set maximum size
        self.central_widget = ImageSelectorWidget()
        self.setCentralWidget(self.central_widget)

        # Main layout
        # main_layout = QHBoxLayout(self.central_widget)
        self.create_dock_windows()
        
    def create_dock_windows(self):
        dock = MapperGeneratorDockwidget()
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)

    def load_image(self):
        file_dialog = QFileDialog()
        image_path, _ = file_dialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if image_path:
            pixmap = QPixmap(image_path)
            self.image_label.setPixmap(pixmap)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.setWindowState(window.windowState() | Qt.WindowMaximized)  # Maximize window
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
