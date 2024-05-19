from PyQt6.QtCore import pyqtSignal, QObject


class ConfigurationClickedEmitter(QObject):
    neighbor_signal = pyqtSignal(int, name="NeighborClick")
    modification_signal = pyqtSignal(int, bool, name="ModificationSignal")
