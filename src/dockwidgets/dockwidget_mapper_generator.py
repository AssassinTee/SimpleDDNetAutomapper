import sys
from PyQt5.QtWidgets import QDockWidget, QHBoxLayout, QVBoxLayout, QRadioButton, QLabel, QPushButton, QFileDialog, QMessageBox
from PyQt5.QtGui import QPixmap
from widgets.widget_mapper_generator import MapperGeneratorWidget


class MapperGeneratorDockwidget(QDockWidget):
    def __init__(self):
        super().__init__()
        self.setWidget(MapperGeneratorWidget())
        self.setFeatures(QDockWidget.DockWidgetMovable|QDockWidget.DockWidgetFloatable)
