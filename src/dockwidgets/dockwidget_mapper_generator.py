from PyQt6.QtWidgets import QDockWidget
from src.widgets.widget_mapper_generator import MapperGeneratorWidget


class MapperGeneratorDockwidget(QDockWidget):
    def __init__(self):
        super().__init__()
        self.setWidget(MapperGeneratorWidget())
        self.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable | QDockWidget.DockWidgetFeature.DockWidgetFloatable)
