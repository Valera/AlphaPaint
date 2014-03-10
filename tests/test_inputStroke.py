from unittest import TestCase
import math
from paint_engine import StrokeInterpolator
# import numpy as np

__author__ = 'vfedotov'


class StrokeInterpolator_test(TestCase):
    def test_serial(self):
        stroke = StrokeInterpolator(5 * math.sqrt(2), 10, 10, 0)
        p1 = stroke.get_next_point()
        self.assertEqual(p1, (10, 10, 0))
        self.assertIsNone(stroke.get_next_point())
        stroke.push_point(20, 20, 1)
        p2 = stroke.get_next_point()
        for a, a_true in zip(p2, (15, 15, 0.5)):
            self.assertAlmostEqual(a, a_true)
        p3 = stroke.get_next_point()
        for a, a_true in zip(p3, (20, 20, 1)):
            self.assertAlmostEqual(a, a_true)
        self.assertIsNone(stroke.get_next_point())
        self.assertAlmostEquals(stroke.offset, 0)
        self.assertAlmostEquals(stroke.prev_x, 20)
        self.assertAlmostEquals(stroke.prev_y, 20)

        stroke.push_point(21, 21, 1)
        self.assertIsNone(stroke.get_next_point())
        self.assertAlmostEquals(stroke.offset, -math.sqrt(2))
        self.assertAlmostEquals(stroke.prev_x, 21)
        self.assertAlmostEquals(stroke.prev_y, 21)
        stroke.push_point(26, 26, 0)
        p4 = stroke.get_next_point()
        for a, a_true in zip(p4, (25, 25, 0.2)):
            self.assertAlmostEqual(a, a_true)

        stroke.push_point(30, 30, 1)
        p5 = stroke.get_next_point()
        for a, a_true in zip(p5, (30, 30, 1)):
            self.assertAlmostEqual(a, a_true)

        stroke.push_point(50, 50, 1)
        for a, a_true in zip(stroke.get_next_point(), (35, 35, 1)):
            self.assertAlmostEqual(a, a_true)
        for a, a_true in zip(stroke.get_next_point(), (40, 40, 1)):
            self.assertAlmostEqual(a, a_true)
        for a, a_true in zip(stroke.get_next_point(), (45, 45, 1)):
            self.assertAlmostEqual(a, a_true)
        for a, a_true in zip(stroke.get_next_point(), (50, 50, 1)):
            self.assertAlmostEqual(a, a_true)

    # def test_get_next_point(self):
        # self.fail()
