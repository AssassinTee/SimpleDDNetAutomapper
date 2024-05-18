from PyQt5.QtGui import QImage, QPainter, QPixmap


class ImageHelper:
    _instance = None

    def __init__(self):
        raise RuntimeError('Call instance() instead')

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        self.CHECKER_IMAGE = QImage("data/img/checker.png").scaled(16, 16)
        self.NO_TILE_FOUND = QPixmap("data/img/tile_not_found.png")

    def drawCheckerImage(self, qp: QPainter, width: int, height: int):
        for y in range(0, height, self.CHECKER_IMAGE.height()):
            for x in range(0, width, self.CHECKER_IMAGE.width()):
                qp.drawImage(x, y, self.CHECKER_IMAGE)
