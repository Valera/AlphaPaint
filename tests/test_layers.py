from unittest import TestCase
from PyQt5.QtGui import QPainter, QImage, QColor
from layers import Layer
from test_tools import show_qimage

__author__ = 'vfedotov'


class TestLayer(TestCase):
    def test_serial(self):
        layer = Layer(10, 20)
        self.assertEqual(layer.width, 10)
        self.assertEqual(layer.height, 20)
        self.assertEqual(layer.image.width(), 10)
        self.assertEqual(layer.image.height(), 20)
        self.assertEqual(layer.alpha, 1)
        self.assertEqual(layer.mode, Layer.NormalMode)
        #self.assertEqual(l)
        #self.assertEqual()
        self.assertEqual(layer.image.pixel(5, 5), QColor(255, 255, 255).rgba())

    def test_drawQImage(self):
        layer = Layer(100, 100)
        qim = QImage(11, 11, QImage.Format_ARGB32)
        qim.fill(0)
        qp = QPainter(qim)
        qp.setBrush(QColor(255, 0, 0))
        qp.drawEllipse(0, 0, 10, 10)
        qp.end()
        layer.drawQImage(20, 20, qim)
        self.assertEqual(layer.image.pixel(25, 25), QColor(255, 0, 0).rgba())
        # show_qimage(layer.image, 2)


        #Mask tests
