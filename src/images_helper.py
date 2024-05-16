from PyQt5.QtGui import QImage, QPainter

CHECKER_IMAGE = QImage("img/checker.png").scaled(16, 16)


def drawCheckerImage(qp: QPainter, width: int, height: int):
    for y in range(0, height, CHECKER_IMAGE.height()):
        for x in range(0, width, CHECKER_IMAGE.width()):
            qp.drawImage(x, y, CHECKER_IMAGE)
