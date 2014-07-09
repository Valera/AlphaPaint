from PyQt5.QtCore import QPoint, QRect
from PyQt5.QtGui import (QImage, QPainter, QColor)

__author__ = 'Valeriy A. Fedotov, valeriy.fedotov@gmail.com'


class Layer:
    NormalMode = 1

    def __init__(self, width, height, color=QColor(255, 255, 255)):
        self.width = width
        self.height = height
        self.image = QImage(width, height, QImage.Format_ARGB32)
        self.image.fill(QColor(color))
        self.alpha = 1
        self.mode = self.NormalMode
        self.updated_rect = None

    def drawQImage(self, x: int, y: int, qimage: QImage):
        image_rect = QRect(x, y, qimage.width(), qimage.height())
        if self.updated_rect is not None:
            # TODO: smarter algorithm of rectangle union or putting both rects in a list
            self.updated_rect = self.updated_rect.united(image_rect)
        else:
            self.updated_rect = image_rect
        qp = QPainter(self.image)
        qp.drawImage(QPoint(x, y), qimage)
        qp.end()

    def pixelColor(self, x, y):
        return QColor(self.image.pixel(x, y))

    def drawUpdatedRect(self, qp: QPainter):
        if self.updated_rect is not None:
            qp.drawImage(QRect(0, 0, self.updated_rect.width(), self.updated_rect.height()),
                         self.image, self.updated_rect)
            self.updated_rect = None

    def composeOnOtherLayers(self, image: QImage):
        assert(self.image.width() == image.width())
        assert(self.image.height() == image.height())

        if self.mode == self.NormalMode:
            with QPainter(image) as p:
                p.drawImage(QRect(0, 0, image.width(), image.height()), self.image)
        else:
            assert(False)


class LayerStack:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.layers = [Layer(width, height)]
        self.cache = QImage(width, height, QImage.Format_ARGB32)
        self.scaleFactor = 1
        self.cacheFullUpdate()
        self.currentInd = 0

    def setScaleFactor(self, scaleFactor):
        self.scaleFactor = scaleFactor
        self.cacheFullUpdate()

    def activeLayer(self):
        return self.layers[self.currentInd]

    def setActiveLayer(self, index):
        self.currentInd = index

    # def move_layer(self, layer_ind, dx, dy):
    #     pass

    def layer_count(self):
        return len(self.layers)

    def add_layer_above(self):
        self.layers.insert(self.currentInd + 1, Layer(self.width, self.height, QColor(0, 0, 0, 0)))

    def deleteCurrentLayer(self):
        self.layers.pop(self.currentInd)
        self.currentInd -= 1

    def move_layer_in_stack(self, old_ind, new_ind):
        assert (0 < old_ind < len(self.layers))
        assert (0 < new_ind < len(self.layers))
        self.layers.insert(new_ind, self.layers.pop(old_ind))

    def cacheFullUpdate(self):
        cacheWidth = self.width * self.scaleFactor
        cacheHeight = self.height * self.scaleFactor
        if self.cache.width() != cacheWidth or self.cache.height() != cacheHeight:
            self.cache = QImage(cacheWidth, cacheHeight, QImage.Format_ARGB32)

        self.cache.fill(QColor(255, 255, 255))
        qp = QPainter(self.cache)
        for layer in self.layers:
            qp.drawImage(QRect(0, 0, cacheWidth, cacheHeight), layer.image)
        qp.end()

    def drawOnDisplayWidget(self, intersected, rect1, qpainter):
        self.cacheFullUpdate() # TODO: smarter update with 3 caches: current, merged_above, merged_below
        qpainter.drawImage(intersected, self.cache, rect1)
