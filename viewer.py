import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QAction
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QScrollArea, QMessageBox

from src.dialogs.dialog_config_settings import ConfigSettingsDialog
from src.dockwidgets.dockwidget_mapper_generator import MapperGeneratorDockwidget
from src.widgets.widget_image_selector import ImageSelectorWidget


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Simple DDNet Automapper")
        self.resize(800, 600)  # Set initial size if needed
        self.central_widget = ImageSelectorWidget(self)
        # scroll_area = QScrollArea(self)
        # scroll_area.setWidget(self.central_widget)
        self.setCentralWidget(self.central_widget)

        # Main layout
        # main_layout = QHBoxLayout(self.central_widget)
        self.create_dock_windows()

        # Create menu bar
        menubar = self.menuBar()

        # Create File menu
        file_menu = menubar.addMenu('&File')

        # Add Open action to File menu
        open_action = QAction('&Open', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.central_widget.select_image)
        file_menu.addAction(open_action)

        # Add Settings action to File menu
        settings_action = QAction('&Settings', self)
        settings_action.triggered.connect(self.openSettings)
        file_menu.addAction(settings_action)

        # Create Help menu
        help_menu = menubar.addMenu('&Help')

        # Add About action to Help menu
        about_action = QAction('&About', self)
        about_action.triggered.connect(self.showAbout)
        help_menu.addAction(about_action)

    def create_dock_windows(self):
        dock = MapperGeneratorDockwidget()
        dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)

    def openSettings(self):
        ConfigSettingsDialog(self).exec()

    def showAbout(self):
        QMessageBox.about(self, 'About', 'This is a PyQt6 menu example.')


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.setWindowState(window.windowState() | Qt.WindowState.WindowMaximized)  # Maximize window
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
