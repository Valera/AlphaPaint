from unittest import TestCase
from layers import LayerStack

__author__ = 'vfedotov'


class TestLayerStack(TestCase):
    def test(self):
        ls = LayerStack(10, 20)
        self.assertEqual(ls.width, 10)
        self.assertEqual(ls.height, 20)