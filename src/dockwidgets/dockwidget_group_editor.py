from PyQt6.QtWidgets import QDockWidget

from src.widgets.widget_group_editor import GroupEditorWidget


class GroupEditorDockwidget(QDockWidget):
    def __init__(self):
        super().__init__("Tile Groups")
        self.setWidget(GroupEditorWidget())
        self.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable | QDockWidget.DockWidgetFeature.DockWidgetFloatable)
