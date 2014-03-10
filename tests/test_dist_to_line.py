from math import sqrt
from unittest import TestCase
from colorcircle import dist_to_line

__author__ = 'vfedotov'


class TestDist_to_line(TestCase):
    def test_dist_to_line(self):
        self.assertEqual(2, dist_to_line(0, 0, 2, 2, 0, 1))
        self.assertAlmostEqual(sqrt(2) / 2, dist_to_line(1, 1, 3, 0, -1, 1))