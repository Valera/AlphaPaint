from PyQt5.QtGui import QColor
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QApplication, QLabel, QWidget
import sys

__author__ = 'vfedotov'

import os

assert(0 == os.system("python3 setup.py install --install-lib ."))

import paint_engine_core

def main():
    app = QApplication(sys.argv)
    im1 = QImage(5, 5, QImage.Format_ARGB32)
    im1.fill(QColor(0,0,0))

    brush = paint_engine_core.SimpleBrush(2.5, 1, 2)
    image = paint_engine_core.Image(5, 5)
    scanLines = [int(im1.scanLine(i)) for i in range(5)]
    image.registerQImageScanLines(scanLines)


    stroke = paint_engine_core.BrushStroke(brush, image, paint_engine_core.Color(1, 0, 0))
    stroke.processMouseMove(0, 0, 0.01)
    stroke.processMouseMove(0, 2, 0.01)
    stroke.processMouseMove(2, 2, 0.01)

    w = QWidget()
    w.show()
    lbl = QLabel(w)

    im2 = QImage(120, 120, QImage.Format_ARGB32)
    im2.fill(QColor(0,180, 0))
    qp = QPainter(im2)
    qp.drawImage(10, 10, im1.scaled(100, 100))
    qp.end()

    lbl.setPixmap(QPixmap(im2))
    lbl.show()
    app.exec_()

if __name__ == "__main__":
    main()