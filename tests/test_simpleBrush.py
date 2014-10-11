from unittest import TestCase

from PyQt5.QtGui import QColor

from layers import Layer
from paint_engine_obsolete import SimpleBrush, SimpleProperties


__author__ = 'vfedotov'


class TestSimpleBrush(TestCase):
    def test_init(self):
        sb = SimpleBrush(Layer(100, 100), SimpleProperties(11, 2, QColor(255, 0, 0), alpha=1))
        # show_qimage(sb.properties.cache_stamp, 10)
        for i in range(11):
            for j in range(11):
                # print(i, j, i, 10 - j)
                c1 = QColor(sb.properties.cache_stamp.pixel(i, j))
                c2 = QColor(sb.properties.cache_stamp.pixel(i, 10 - j))
                self.assertLess(abs(c1.red() - c2.red()), 3)
                self.assertLess(abs(c1.green() - c2.green()), 3)
                self.assertLess(abs(c1.blue() - c2.blue()), 3)
                # self.assertEqual(
