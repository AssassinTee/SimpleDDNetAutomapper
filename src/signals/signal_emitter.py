from PyQt5.QtCore import pyqtSignal, QObject


class NeighborClickedEmitter(QObject):
    neighbor_signal = pyqtSignal(int, name="NeighborClick")
