from unittest import TestCase

from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QImage, QPainter, QColor

from layers import LayerStack


__author__ = 'vfedotov'


def makeQIMageWithCircle(w, h, x, y, R, color):
    im = QImage(w, h, QImage.Format_ARGB32)
    im.fill(QColor(0, 0, 0, 0))
    p = QPainter(im)
    p.setPen(QColor(color))
    p.setBrush(QColor(color))
    p.drawEllipse(QPointF(x, y), R, R)
    p.end()
    # show_qimage(im)
    return im


class TestLayerStack(TestCase):
    def test(self):
        ls = LayerStack(10, 20)
        self.assertEqual(ls.width, 10)
        self.assertEqual(ls.height, 20)

    def test_two_layers(self):
        ls = LayerStack(100, 100)
        ls.add_layer_above()
        self.assertEqual(ls.layer_count(), 2)
        col1 = QColor(255, 0, 0)
        im1 = makeQIMageWithCircle(100, 100, 60, 60, 39, col1)
        col2 = QColor(0, 0, 255)
        im2 = makeQIMageWithCircle(100, 100, 39, 39, 39, col2)
        ls.activeLayer().drawQImage(0, 0, im1)
        ls.layers[1].drawQImage(0, 0, im2)
        ls.cacheFullUpdate()
        self.assertEqual(ls.cache.pixel(50, 50), col2.rgba())
        self.assertEqual(ls.cache.pixel(80, 80), col1.rgba())
        self.assertEqual(ls.cache.pixel(90, 10), 0xFFFFFFFF)
        # show_qimage(ls.cache, 4)

    def test_layers_adding_and_deleting(self):
        ls = LayerStack(10, 10)
        ls.add_layer_above()
        ls.add_layer_above()
        a, b, c = ls.layers
        ls.deleteCurrentLayer()
        b1, c1 = ls.layers
        self.assertIs(b, b1)
        self.assertIs(c, c1)

        ls.add_layer_above()
        a, b, c = ls.layers
        ls.setActiveLayer(1)
        ls.deleteCurrentLayer()
        a1, c1 = ls.layers
        self.assertIs(a, a1)
        self.assertIs(c, c1)
