import sys
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QAction
from PyQt6.QtWidgets import QMainWindow, QFileDialog, QScrollArea, QMessageBox

from src.dialogs.dialog_config_settings import ConfigSettingsDialog
from src.dockwidgets.dockwidget_group_editor import GroupEditorDockwidget
from src.dockwidgets.dockwidget_mapper_generator import MapperGeneratorDockwidget
from src.widgets.widget_image_selector import ImageSelectorWidget
from src.config.app_state import AppState
from src.signals.signal_emitter import ApplicationStatusEnum
from src.backend import blueprint
from src.backend.blueprint import Blueprint
from src.backend.group_handler import GroupHandler
from src.backend.tile_handler import TileHandler
from src.logger import BroadErrorHandler
import src.logger
import logging
logger = logging.getLogger(__name__)


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
        self.mapper_generator = MapperGeneratorDockwidget()
        self.mapper_generator.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.mapper_generator)
        self.mapper_generator.setDisabled(True)  # disable until image is loaded

        self.group_editor = GroupEditorDockwidget()
        self.group_editor.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.group_editor)
        self.group_editor.setDisabled(True)  # disable until image is loaded

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

        file_menu.addSeparator()

        load_blueprint_action = QAction('&Load Blueprint', self)
        load_blueprint_action.triggered.connect(self.loadBlueprint)
        file_menu.addAction(load_blueprint_action)

        save_blueprint_action = QAction('&Save Blueprint', self)
        save_blueprint_action.triggered.connect(self.saveBlueprint)
        file_menu.addAction(save_blueprint_action)

        # Create Help menu
        help_menu = menubar.addMenu('&Help')

        # Add About action to Help menu
        about_action = QAction('&About', self)
        about_action.triggered.connect(self.showAbout)
        help_menu.addAction(about_action)

        # connect app to app state signal emitter
        AppState.instance().signal_emitter.application_status_signal.connect(self.statusUpdateReceived)

    def openSettings(self):
        ConfigSettingsDialog(self).exec()
        self.mapper_generator.widget().refreshClientButton()

    @BroadErrorHandler(logger)
    def saveBlueprint(self, checked=False) -> bool:
        image_path = AppState.imagePath()
        if not image_path:
            AppState.setStatus(ApplicationStatusEnum.WARNING, "Load a tileset image first.")
            return False

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save blueprint", f"{image_path.stem}.blueprint.json", "Blueprint (*.json)")
        if not file_path:
            return False

        bp = Blueprint(TileHandler.instance().getAllTileData(), image_path.stem, GroupHandler.instance().getGroups())
        Path(file_path).write_text(blueprint.dumps(bp))
        AppState.setStatus(ApplicationStatusEnum.INFO, f"Blueprint saved to {file_path}")
        return True

    @BroadErrorHandler(logger)
    def loadBlueprint(self, checked=False):
        image_path = AppState.imagePath()
        if not image_path:
            AppState.setStatus(ApplicationStatusEnum.WARNING, "Load a tileset image first.")
            return

        file_path, _ = QFileDialog.getOpenFileName(self, "Load blueprint", "", "Blueprint (*.json)")
        if not file_path:
            return

        bp = blueprint.loads(Path(file_path).read_text())
        if bp.image and bp.image != image_path.stem:
            AppState.setStatus(ApplicationStatusEnum.WARNING,
                               f"Blueprint was saved for '{bp.image}', tiles may not match.")

        tiles = self.central_widget.tileClicker().tiles
        for tile_id, tile_data in bp.tiles.items():
            tile = tiles[tile_id]
            tile.tile_data = tile_data
            tile.tile_checked = 1
            tile.lock = False
            TileHandler.instance().updateTileStorage(tile)
            tile.update()

        GroupHandler.instance().setGroups(bp.groups)
        AppState.groupsChanged()
        AppState.setStatus(ApplicationStatusEnum.INFO, f"Blueprint loaded from {file_path}")

    def showAbout(self):
        QMessageBox.about(self, 'About', 'This is a PyQt6 menu example.')

    def statusUpdateReceived(self, status_type: ApplicationStatusEnum, message: str):
        logger.debug(f"Status update received: {status_type}{', ' if len(message) else ''}{message}")
        if status_type == ApplicationStatusEnum.IMAGE_LOADED:
            self.mapper_generator.setEnabled(True)
            self.mapper_generator.widget().rulesLoaded()
            self.group_editor.setEnabled(True)
        elif status_type == ApplicationStatusEnum.RESET_APP:
            self.mapper_generator.widget().reset()
            self.central_widget.reset()
            TileHandler.instance().reset()
            GroupHandler.instance().reset()
            self.group_editor.widget().reset()
            self.group_editor.setDisabled(True)
        elif status_type == ApplicationStatusEnum.GROUPS_CHANGED:
            self.group_editor.widget().refresh()
            self.central_widget.tileClicker().refreshGroups()
        elif status_type in (ApplicationStatusEnum.WARNING, ApplicationStatusEnum.INFO):
            self.statusBar().showMessage(message, 8000)
