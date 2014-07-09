from threading import _MainThread
from PyQt5.QtCore import QPointF, Qt

from layers import Layer


__author__ = 'Valeriy A. Fedotov, valeriy.fedotov@gmail.com'

from queue import Queue
import math
from PyQt5.QtGui import (QImage, QPainter, QColor, QBrush, QRadialGradient)


class StrokeInterpolator:
    def __init__(self, spacing, x0, y0, pressure0):
        self.spacing = spacing
        self.prev_x = x0
        self.prev_y = y0
        self.prev_pressure = pressure0
        self.offset = 0
        self.queue = Queue()
        self.queue.put((x0, y0, pressure0))
        self.start_ind = 1

    def push_point(self, x, y, pressure):
        dx = x - self.prev_x
        dy = y - self.prev_y
        d_pressure = pressure - self.prev_pressure
        length = math.hypot(dx, dy)

        if length == 0:
            return

        if length < self.offset:
            self.offset -= length
            self.prev_x = x
            self.prev_y = y
            self.prev_pressure = pressure
            return

        count = int((length - self.offset) / self.spacing)
        x0 = self.prev_x + self.offset * dx / length
        y0 = self.prev_y + self.offset * dy / length
        pressure0 = self.prev_pressure + self.offset * d_pressure / length
        # print('x0, y0', x0, y0)
        for i in range(self.start_ind, count + 1):
            interpolation_parameter = i * self.spacing / length
            x1 = x0 + dx * interpolation_parameter
            y1 = y0 + dy * interpolation_parameter
            # print(interpolation_parameter, x1, y1, self.prev_pressure, pressure)
            pressure1 = pressure0 + d_pressure * interpolation_parameter
            self.queue.put((x1, y1, pressure1))
        self.offset = count * self.spacing + self.offset - length
        self.start_ind = 1
        self.prev_x = x
        self.prev_y = y
        self.prev_pressure = pressure

    def get_next_point(self):
        if not self.queue.empty():
            return self.queue.get()
        return None

    def push_end_point(self, x_end, y_end, pressure_end):
        self.push_point(x_end, y_end, pressure_end)

# def notimpl(message):
#     def wrapper(fun):
#         raise NotImplementedError(
#             "{} must be implemented in subclasses of {}".format())


class BrushPropertiesInterface:
    """
    Storage for current brush properties and cache.
    """

    def __init__(self):
        raise NotImplementedError

    # def __setattr__(self, key, value):
    #     setattr(self, key, value)
    #     self.update_cache(key)

    def update_cache(self):
        raise NotImplementedError

    def update_cache_for_key(self, key):
        raise NotImplementedError

    def properties(self):
        raise NotImplementedError

    def restore_defaults(self):
        raise NotImplementedError

    def serialize(self):
        raise NotImplementedError


class BrushInterface:
    def __init__(self, brush_properties):
        raise NotImplementedError

    def start_stroke(self, x, y, pressure):
        raise NotImplementedError

    def continue_stroke(self, x, y, pressure):
        raise NotImplementedError

    def end_stroke(self, x, y, pressure):
        raise NotImplementedError


# TODO: Move brush settings to a class property
class SimpleProperties(BrushPropertiesInterface):
    def __init__(self, size, spacing, color, hardness=0.0, alpha=0.3):
        self.props = {'size': size, 'spacing': spacing, 'hardness': hardness, 'alpha': alpha}
        self.color = color
        self.update_cache()

    def update_cache(self):
        size = self.props['size']
        self.cache_stamp = QImage(size, size, QImage.Format_ARGB32)
        self.cache_stamp.fill(QColor(0, 0, 0, 0))
        # TODO: move all painting to 'with' statements
        p = QPainter(self.cache_stamp)
        p.setRenderHint(QPainter.Antialiasing, True)
        grad = QRadialGradient(QPointF(size/2, size/2), 1.0 * size/2)
        color1 = QColor(self.color)
        color1.setAlpha(self.props['alpha'])
        color2 = QColor(self.color)
        color2.setAlpha(self.props['alpha'] * self.props['hardness'] / 255)
        grad.setColorAt(0, color1)
        grad.setColorAt(1, color2)
        br = QBrush(grad)
        p.setBrush(br)
        p.setPen(Qt.NoPen)
        p.drawEllipse(0, 0, size, size)
        p.end()
        # self.cache_stamp.fill(QColor(0, 0, 255))

    def update_cache_for_key(self, key):
        self.update_cache()

    def properties(self):
        return ['size', 'spacing', 'hardness', 'alpha']

    def propertyDescriptions(self):
        return [
            PropertyDescription('Size', 1, 500, 20, lambda x: self.setBrushProperty('size', x)),
            PropertyDescription('Opacity', 0, 255, 255, lambda x: self.setBrushProperty('alpha', x)),
            PropertyDescription('Hardness', 0, 255, 255, lambda x: self.setBrushProperty('hardness', x)),
            PropertyDescription('Spacing', 1, 20, 10, lambda x: self.setBrushProperty('spacing', x))
        ]

    def restore_defaults(self):
        return super().restore_defaults()

    def brush_property(self, property_name):
        return self.props[property_name]

    def setBrushProperty(self, property, value):
        self.props[property] = value
        if property != 'spacing':
            self.update_cache()

    def serialize(self):
        return super().serialize()


class SimpleBrush(BrushInterface):
    def __init__(self, canvas: Layer, brush_properties: SimpleProperties):
        self.properties = brush_properties
        self.canvas = canvas

    def start_stroke(self, x, y, pressure):
        self.interpolator = StrokeInterpolator(self.properties.brush_property('spacing'), x, y, pressure)
        self.draw_to_new_point()

    def continue_stroke(self, x, y, pressure):
        self.interpolator.push_point(x, y, pressure)
        self.draw_to_new_point()

    def end_stroke(self, x, y, pressure):
        self.interpolator.push_point(x, y, pressure)
        self.draw_to_new_point()

    def draw_to_new_point(self):
        print("draw_to_new_point")
        # p = QPainter(self.canvas)
        while True:
            next_point = self.interpolator.get_next_point()
            print("next_point", next_point)
            if next_point is None:
                break
            x, y, pressure = next_point
            size = self.properties.brush_property('size')
            size = math.ceil(size * pressure)
            x, y = x - size // 2, y - size // 2
            print("drawing at", x, y)
            self.canvas.drawQImage(x, y, self.properties.cache_stamp)
            # p.drawImage(x, y, self.properties.cache_stamp)
            # p.end()


class PropertyDescription:
    def __init__(self, name, min, max, default, updater, editorType='slider'):
        """
        Storage Class for brush properties.

        @param name: name of property, string
        @param min: minimal value for graphical control
        @param max: maximal value
        @param default: default value for graphical control
        @param updater: function of one parameter that is called to update property of th
            current brush
        @param editorType: graphical control type
        """
        self.name = name
        self.min = min
        self.max = max
        self.default = default
        self.editorType = editorType
        self.updater = updater

        # TODO: decide how to switch between different brush presets.