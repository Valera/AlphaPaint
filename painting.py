__author__ = 'Valeriy A. Fedotov, valeriy.fedotov@gmail.com'

from PyQt5.QtCore import (QSize, QPoint, QRect, Qt, QPointF)
from PyQt5.QtWidgets import (QWidget, QScrollArea)
from PyQt5.QtGui import (QImage, QPainter, QColor, QMouseEvent, QPaintEvent, QKeyEvent, QCursor, QPixmap, QBitmap)

import paint_engine
from layers import LayerStack, Layer


class CustomScrollArea(QScrollArea):
    DragMode = 1
    NormalMode = 2

    def __init__(self):
        super().__init__()
        # self.setAttribute(Qt.WA_KeyCompression, True)

    def setWidget(self, w: QWidget):
        """
        Add widget and center it
        @param w: widget to add
        """
        super().setWidget(w)
        hsb = self.horizontalScrollBar()
        hsb.setValue(0.5 * (hsb.minimum() + hsb.maximum()))
        vsb = self.verticalScrollBar()
        vsb.setValue(0.5 * (vsb.minimum() + vsb.maximum()))

    def keyPressEvent(self, e: QKeyEvent):
        if e.isAutoRepeat():
            return
        if e.text() == ' ':
            print('Entering DragMode')
            self.mode = self.DragMode
            self.widget().setMouseInteraction(False)
        elif e.text() == '+':
            print('got +')
            self.zoomFactor = self.widget().zoomIn()
        elif e.text() == '-':
            print('got -')
            self.zoomFactor = self.widget().zoomOut()
        elif e.text() == ']':
            self.widget().increaseBrushSize()
        elif e.text() == '[':
            self.widget().decreaseBrushSize()
        else:
            return super().keyPressEvent(e)

    def keyReleaseEvent(self, e: QKeyEvent):
        if e.isAutoRepeat():
            return
        if e.text() == ' ':
            print('Back to NormalMode')
            self.mode = self.NormalMode # FIXME: correct work if space is released before dragging ends.
            self.widget().setMouseInteraction(True)
        else:
            return super().keyPressEvent(e)

    def mousePressEvent(self, e: QMouseEvent):
        print(456)
        if self.mode == self.NormalMode:
            return super().mousePressEvent(e)
        print('123')
        self.baseSBX = self.horizontalScrollBar().value()
        self.baseSBY = self.verticalScrollBar().value()
        self.baseX = e.x()
        self.baseY = e.y()

    def mouseMoveEvent(self, e: QMouseEvent):
        if self.mode == self.NormalMode:
            return super().mouseMoveEvent(e)
        self.horizontalScrollBar().setValue(self.baseSBX - e.x() + self.baseX)
        self.verticalScrollBar().setValue(self.baseSBY - e.y() + self.baseY)


class PaintWidget(QWidget):
    BORDER = 500 # TODO: change border dynamically when window size is changed.

    def __init__(self, width, height):
        super().__init__()
        self.mouseEnabled = 1
        self.zoomFactor = 1
        self.layerStack = LayerStack(width, height)
        self.zoomFactorsArray = [0.25, 0.5, 1, 2, 4]
        self.zoomIndex = self.zoomFactorsArray.index(1)
        self.__adjustSize()
        self.brushColor = QColor(0, 0, 0)
        self.brush_properties = paint_engine.SimpleProperties(32, 1.5, self.brushColor)
        # p = QPainter(self.canvas)
        # p.drawEllipse(0, 0, width, height)
        self.mode = None
        self.updateBrushCursor()

    def updateBrushCursor(self):
        size = min(64, self.brush_properties.props['size'])
        pmap = QPixmap(size, size)
        pmap.fill(QColor(0, 0, 0, 0))
        p = QPainter(pmap)
        p.drawEllipse(0, 0, size - 1, size - 1)
        p.end()
        self.setCursor(QCursor(pmap))

    def setBrushHSV(self, h, s, v):
        self.brushColor = QColor.fromHsv(h, s, v)
        self.brush_properties.color = self.brushColor
        self.brush_properties.update_cache()

    def __adjustSize(self):
        self.canvasWidth = self.layerStack.width * self.zoomFactor
        print('new canvas witdth:', self.canvasWidth)
        self.canvasHeight = self.layerStack.height * self.zoomFactor
        self.setFixedSize(QSize(self.canvasWidth + 2 * self.BORDER, self.canvasHeight + 2 * self.BORDER))

    def zoomIn(self):
        self.zoomIndex = min(self.zoomIndex + 1, len(self.zoomFactorsArray) - 1)
        self.zoomFactor = self.zoomFactorsArray[self.zoomIndex]
        self.layerStack.setScaleFactor(self.zoomFactor)
        self.__adjustSize()
        return self.zoomFactor

    def zoomOut(self):
        self.zoomIndex = max(0, self.zoomIndex - 1)
        self.zoomFactor = self.zoomFactorsArray[self.zoomIndex]
        self.layerStack.setScaleFactor(self.zoomFactor)
        self.__adjustSize()
        return self.zoomFactor

    def paintEvent(self, e: QPaintEvent):

        canvasRect = QRect(self.BORDER, self.BORDER, self.canvasWidth, self.canvasHeight)
        rect = QRect(e.rect())
        rectCopy = QRect(rect)
        intersected = canvasRect.intersected(rect)
        # rect1 = QRect(self.canvasWidth - intersected.width(), self.canvasHeight - intersected.height(),
        #               intersected.width(), intersected.height())
        rect1 = QRect(0, 0, self.canvasWidth, self.canvasHeight)
        x = intersected.x()
        x = x - self.BORDER if x > self.BORDER else 0
        y = intersected.y()
        y = y - self.BORDER if y > self.BORDER else 0
        rect1.setX(x)
        rect1.setY(y)
        rect1.setWidth(intersected.width())
        rect1.setHeight(intersected.height())

        print(intersected, rect1)
        # rect.moveTo(self.BORDER, self.BORDER)
        p = QPainter(self)
        p.setBrush(QColor(200, 200, 200))
        p.setPen(QColor(200, 200, 200))
        p.drawRect(rectCopy)
        self.layerStack.drawOnDisplayWidget(intersected, rect1, p)
        p.end()

    def setMouseInteraction(self, isEnabled):
        self.setAttribute(Qt.WA_NoMousePropagation, isEnabled)
        self.mouseEnabled = isEnabled

    def mousePressEvent(self, e: QMouseEvent):
        if not self.mouseEnabled:
            return super().mousePressEvent(e)

        if self.mode == 'drag':
            self.dragStart = e.x(), e.y()
            return

        modifiers = e.modifiers()
        # print(modifiers &

        self.brush = paint_engine.SimpleBrush(self.layerStack.activeLayer(), self.brush_properties)
        self.brush.start_stroke((e.x() - self.BORDER) / self.zoomFactor, (e.y() - self.BORDER) / self.zoomFactor, 1)
        self.update()  # FIXME: ineffective

    def mouseMoveEvent(self, e: QMouseEvent):
        if not self.mouseEnabled:
            return super().mouseMoveEvent(e)
        if self.mode == 'drag':
            print(1234)
            self.setGeometry(10, 10, 10, 10)

        self.brush.continue_stroke((e.x() - self.BORDER) / self.zoomFactor, (e.y() - self.BORDER) / self.zoomFactor, 1)
        self.update()

    def mouseReleaseEvent(self, e: QMouseEvent):
        if not self.mouseEnabled:
            return super().mouseReleaseEvent(e)

        self.brush.end_stroke((e.x() - self.BORDER) / self.zoomFactor, (e.y() - self.BORDER) / self.zoomFactor, 1)
        self.update()

    def increaseBrushSize(self):
        self.brush_properties.props['size'] += 5
        self.brush_properties.update_cache()
        self.updateBrushCursor()

    def decreaseBrushSize(self):
        print('decrease')
        self.brush_properties.props['size'] -= 5
        self.brush_properties.update_cache()
        self.updateBrushCursor()
        # self.unsetCursor()

    def tabletEvent(self, tabletEvent):
        pass
    #
    # def keyPressEvent(self, e: QKeyEvent):
    #     if e.text() == ' ':
    #         print("space")
    #         self.mode = 'drag'
    #
    # def keyReleaseEvent(self, QKeyEvent):
    #     if e.text() == ' ':
    #         self.mode = None



class PaintingInterface:
    def __init__(self):
        pass

    def change_size(self, size):
        pass

    def set_border(self, size, style):
        pass

    def save(self, filename):
        pass

    def load(self, filename):
        pass


class LayerInterface:
    def __init__(self, width, height):
        pass

    def set_application_mode(self, mode):
        pass

    def apply_to(self, other_layer):
        pass

    def draw_brush_stamp(self):
        pass