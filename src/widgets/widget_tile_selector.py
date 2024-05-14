from PyQt5.QtWidgets import QLabel

class TileSelector(QLabel):
    def __init__(self, id, handler, parent=None):
        super().__init__(parent)
        
        self.id = id
        self.handler = handler
        
        self.mousePressEvent = self.onClick()
        self._state = 0
        self._maxState = 3
        
    def onClick(self):
        self._state += 1
        self._state %= self._maxState