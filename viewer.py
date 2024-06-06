import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QAction
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QScrollArea, QMessageBox

from src.dialogs.dialog_config_settings import ConfigSettingsDialog
from src.dockwidgets.dockwidget_mapper_generator import MapperGeneratorDockwidget
from src.widgets.widget_image_selector import ImageSelectorWidget
from src.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.setWindowState(window.windowState() | Qt.WindowState.WindowMaximized)  # Maximize window
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
