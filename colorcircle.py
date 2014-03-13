from math import floor, ceil, hypot, pi, atan2, sqrt, radians, cos, sin
import sys

from PyQt5.QtCore import QPointF, Qt, QSize, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPen, QMouseEvent, QImage
from PyQt5.QtWidgets import QWidget, QApplication


__author__ = 'vfedotov'


def atan2_in_degs(y, x):
    return (360 * atan2(y, x) / (2 * pi) + 180 + 360) % 360


def dist_to_line(x_probed, y_probed, x_base, y_base, dx, dy):
    vec_x = x_probed - x_base
    vec_y = y_probed - y_base
    return abs(vec_x * dy - vec_y * dx) / hypot(dx, dy)


class ColorCircle(QWidget):
    HSVChanged = pyqtSignal(int, int, int)
    colorChanged = pyqtSignal(QColor)

    def __init__(self, hue: int, saturation: int, value: int):
        super().__init__()
        self.h = hue
        self.s = saturation
        self.v = value
        self.cachedHeight = self.cachedWidth = -1
        self.cachedH = None
        self.updateCache()

    def paintEvent(self, e):
        self.updateCache()
        print('updated')
        w = self.width()
        h = self.height()
        L = min(w, h)
        p = QPainter(self)
        p.drawImage(0, 0, self.cache)

        p.translate(self.width() / 2, self.height() / 2)

        p.setPen(QPen(QColor(255, 255, 255), 2))
        p.drawEllipse(QPointF(0.42 * L * cos(radians(self.h) - pi), 0.42 * L * sin(radians(self.h) - pi)),
                      0.015 * L, 0.015 * L)

        R_sqr = 0.38 * L
        halfSide = R_sqr * sqrt(2) / 2
        y0, y1 = floor(-halfSide), ceil(halfSide)
        x0, x1 = floor(-halfSide), ceil(halfSide)
        y = y1 - self.v * (y1 - y0) / 255
        x = x0 + self.s * (x1 - x0) / 255
        p.setPen(QPen(QColor(255, 255, 255), 2))
        p.drawEllipse(QPointF(x, y), 0.015 * L, 0.015 * L)

        # Rect with color sample
        p.setBrush(QColor.fromHsv(self.h, self.s, self.v))
        p.setPen(QPen(QColor(0, 0, 0), 2))
        p.drawRect(0.35 * L, 0.35 * L, 0.10 * L, 0.10 * L)
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(QColor(0, 0, 0), 1))
        p.end()

    def updateCache(self):
        if self.width() == self.cachedWidth and self.height() == self.cachedHeight and self.h == self.cachedH:
            return
        self.cachedH = self.h
        self.cachedWidth = self.width()
        self.cachedHeight = self.height()
        print('Cached', self.cachedHeight, self.cachedWidth)
        self.cache = QImage(self.width(), self.height(), QImage.Format_ARGB32)

        w = self.width()
        h = self.height()
        L = min(w, h)

        p = QPainter(self.cache)
        p.setBrush(QColor(200, 200, 200))
        p.drawRect(0, 0, w, h)
        p.setBrush(Qt.NoBrush)

        p.translate(w/2, h/2)

        p.setRenderHint(QPainter.Antialiasing, True)
        R_out = 0.44 * L
        R_in = 0.4 * L
        p.drawEllipse(QPointF(0, 0), R_in, R_in)
        p.drawEllipse(QPointF(0, 0), R_out, R_out)
        # FIXME: slow...
        for y in range(floor(-R_out), ceil(R_out) + 1):
            if abs(y) > R_in:
                x0 = 0
            else:
                x0 = floor(sqrt(R_in * R_in - y * y))
            if abs(y) > R_out:
                continue
            else:
                x1 = ceil(sqrt(R_out * R_out - y * y))
            for x in range(x0, x1):
                p.setPen(QColor.fromHsv(atan2_in_degs(y, x), 255, 255))
                p.drawPoint(x, y)
                p.setPen(QColor.fromHsv(atan2_in_degs(y, -x), 255, 255))
                p.drawPoint(-x, y)
            # for x in range(floor(-R_out), ceil(R_out) + 1):
            #     if R_in < hypot(x, y) < R_out:
            #         p.setPen(QColor.fromHsv(atan2_in_degs(y, x), 255, 255))
            #         p.drawPoint(x, y)

        p.setPen(QPen(QColor(0, 0, 0), 3))
        p.drawEllipse(QPointF(0, 0), R_in, R_in)
        p.drawEllipse(QPointF(0, 0), R_out, R_out)
        # p.setPen(QPen(QColor(0, 0, 0), 1))
        # Triangle
        # R_tr = 0.38 * L
        #
        # p.drawLine(p1, p2)       p.scale(1, -1)
        # a = R_tr * sqrt(3)
        # h = sqrt(3) / 2 * a
        # p0 = QPointF(-a / 2, -R_tr / 2)
        # p1 = QPointF(a / 2, -R_tr / 2)
        # p2 = QPointF(0, R_tr)
        # p.drawLine(p0, p1)
        # p.drawLine(p2, p0)
        # for y in range(floor(-R_tr / 2), ceil(R_tr)):
        #     s = y - floor(-R_tr / 2) / (ceil(R_tr) - floor(-R_tr / 2))
        #     for x in range(floor(-a/2), 0):
        #         v =
        #     for x in range(ceil(a/2)):
        #         pass

        p.setPen(QPen(QColor(0, 0, 0), 4))
        R_sqr = 0.38 * L
        halfSide = R_sqr * sqrt(2) / 2
        y0, y1 = floor(-halfSide), ceil(halfSide)
        x0, x1 = floor(-halfSide), ceil(halfSide)
        p.drawRect(x0, y0, (x1 - x0), (y1 - x0))
        for y in range(y0, y1):
            v = 255 * (y1 - y) / (y1 - y0)
            for x in range(x0, x1):
                s = 255 * (x - x0) / (x1 - x0)
                p.setPen(QColor.fromHsv(self.h, s, v))
                p.drawPoint(x, y)

        p.end()

    def mousePressEvent(self, e: QMouseEvent):
        self.activeElement = None
        self.processColorSelection(e)

    def processColorSelection(self, e: QMouseEvent):
        x, y = e.x(), e.y()
        w, h = self.width(), self.height()
        L = min(w, h)
        R_out = 0.44 * L
        R_in = 0.40 * L
        R_sqr = 0.38 * L
        halfSide = ceil(R_sqr * sqrt(2) / 2)
        dx, dy = x - w / 2, y - h / 2
        print(dx, dy)
        if R_in < hypot(dx, dy) < R_out and self.activeElement is None or self.activeElement == 'ring':
            self.h = atan2_in_degs(dy, dx)
            self.HSVChanged.emit(self.h, self.s, self.v)
            self.activeElement = 'ring'
            self.update()
            return
        if abs(dx) < halfSide and abs(dy) < halfSide and self.activeElement is None or self.activeElement == 'square':
            self.v = 255 * (halfSide - dy) / (2 * halfSide)
            self.s = 255 * (dx + halfSide) / (2 * halfSide)
            self.v = min(255, max(0, self.v))
            self.s = min(255, max(0, self.s))
            self.HSVChanged.emit(self.h, self.s, self.v)
            self.activeElement = 'square'
            self.update()

    def mouseMoveEvent(self, e: QMouseEvent):
        self.processColorSelection(e)

    def setColor(self, color: QColor):
        """
        Sets new color for color circle. Updates color circle display,
        emits HSVChanged signal if color has actually changed.

        @param color: new color
        """
        print('newColor!!!')
        hsv = (color.hue(), color.saturation(), color.value())
        oldHSV = self.h, self.s, self.v
        self.h, self.s, self.v = hsv
        if self.s == 0:
            self.h = oldHSV[0]
        if hsv != oldHSV:
            self.HSVChanged.emit(*hsv)
            self.updateCache()
            self.update()

    def sizeHint(self):
        return QSize(200, 200)


def main():
    app = QApplication(sys.argv)
    w = ColorCircle(0, 0, 0)
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
