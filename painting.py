import sys

import ui


__author__ = 'Valeriy A. Fedotov, valeriy.fedotov@gmail.com'

from PyQt5.QtCore import (QSize, QRect, Qt, pyqtSignal)
from PyQt5.QtWidgets import (QWidget, QScrollArea, QDialog, QApplication)
import PyQt5.QtWidgets
from PyQt5.QtGui import (QPainter, QColor, QMouseEvent, QPaintEvent, QKeyEvent, QCursor, QPixmap, QTabletEvent)

import paint_engine_obsolete
from layers import LayerStack


class CustomScrollArea(QScrollArea):
    DragMode = 1
    NormalMode = 2

    def __init__(self):
        super().__init__()
        self.mode = self.NormalMode
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
        elif e.modifiers() & Qt.AltModifier:
            return self.widget().keyPressEvent(e)
        else:
            return super().keyPressEvent(e)

    def keyReleaseEvent(self, e: QKeyEvent):
        if e.isAutoRepeat():
            return
        if e.text() == ' ':
            print('Back to NormalMode')
            self.mode = self.NormalMode # FIXME: correct work if space is released before dragging ends.
            self.widget().setMouseInteraction(True)
        elif e.text() == '':
            return self.widget().keyPressEvent(e)
        else:
            return super().keyPressEvent(e)

    def mousePressEvent(self, e: QMouseEvent):
        if self.mode == self.NormalMode:
            return super().mousePressEvent(e)
        self.baseSBX = self.horizontalScrollBar().value()
        self.baseSBY = self.verticalScrollBar().value()
        self.baseX = e.x()
        self.baseY = e.y()

    def mouseMoveEvent(self, e: QMouseEvent):
        if self.mode == self.NormalMode:
            return super().mouseMoveEvent(e)
        self.horizontalScrollBar().setValue(self.baseSBX - e.x() + self.baseX)
        self.verticalScrollBar().setValue(self.baseSBY - e.y() + self.baseY)

    def tabletEvent(self, e: QTabletEvent):
        e.accept()


class PaintWidget(QWidget):
    BORDER = 500 # TODO: change border dynamically when window size is changed.

    colorChanged = pyqtSignal(QColor)

    def __init__(self, width, height):
        super().__init__()
        self.mouseEnabled = 1
        self.zoomFactor = 1
        self.layerStack = LayerStack(width, height)
        self.zoomFactorsArray = [0.25, 0.5, 1, 2, 4]
        self.zoomIndex = self.zoomFactorsArray.index(1)
        self.__adjustSize()
        self.brushColor = QColor(0, 0, 0)
        self.brush_properties = paint_engine_obsolete.SimpleProperties(32, 1.5, self.brushColor)
        # p = QPainter(self.canvas)
        # p.drawEllipse(0, 0, width, height)
        self.mode = None
        self.inBrushStroke = False
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

    def setBrushColor(self, color):
        self.brushColor = QColor(color)
        self.brush_properties.color = self.brushColor
        self.brush_properties.update_cache()
        self.colorChanged.emit(self.brushColor)

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

    def widgetCoordinatesOnCanvas(self, widgetX, widgetY):
        return (widgetX - self.BORDER) / self.zoomFactor, (widgetY - self.BORDER) / self.zoomFactor

    def mousePressEvent(self, e: QMouseEvent):
        print('mousePressEvent')

        if not self.mouseEnabled:
            return super().mousePressEvent(e)
        if PyQt5.QtWidgets.qApp.stylusIsNearTablet:
            return

        if self.mode == 'drag':
            self.dragStart = e.x(), e.y()
            return

        if Qt.AltModifier & e.modifiers():
            x, y = self.widgetCoordinatesOnCanvas(e.x(), e.y())
            # TODO: Pixel color with regard to zoom.
            color = self.layerStack.activeLayer().pixelColor(x, y)
            self.setBrushColor(color)
            print('new color', color)
            return


        # print(modifiers &

        self.brush = paint_engine_obsolete.SimpleBrush(self.layerStack.activeLayer(), self.brush_properties)
        x, y = self.widgetCoordinatesOnCanvas(e.x(), e.y())
        self.brush.start_stroke(x, y, 1)
        self.update()  # FIXME: ineffective

    def mouseMoveEvent(self, e: QMouseEvent):
        print('mouseMoveEvent')

        if not self.mouseEnabled:
            return super().mouseMoveEvent(e)
        if PyQt5.QtWidgets.qApp.stylusIsNearTablet:
            return

        if Qt.AltModifier & e.modifiers():
            return
        if self.mode == 'drag':
            print(1234)
            self.setGeometry(10, 10, 10, 10)

        x, y = self.widgetCoordinatesOnCanvas(e.x(), e.y())
        self.brush.continue_stroke(x, y, 1)
        self.update()

    def mouseReleaseEvent(self, e: QMouseEvent):
        print('mouseReleaseEvent')

        if not self.mouseEnabled:
            return super().mouseReleaseEvent(e)
        if PyQt5.QtWidgets.qApp.stylusIsNearTablet:
            return

        if Qt.AltModifier & e.modifiers():
            return

        x, y = self.widgetCoordinatesOnCanvas(e.x(), e.y())
        self.brush.end_stroke(x, y, 1)
        self.brush = None
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

    def tabletEvent(self, e: QTabletEvent):
        print('tabletEvent')
        # e.accept()
        # return
        # if not self.mouseEnabled:
        #     e.ignore()
        #     return
        posF = e.posF()
        x, y = self.widgetCoordinatesOnCanvas(posF.x(), posF.y())
        if e.pressure() == 0:
            if self.inBrushStroke:
                self.setMouseInteraction(True)
                self.inBrushStroke = False
                self.brush.end_stroke(x, y, e.pressure())
                self.brush = None
            e.accept()
            self.update()
            return
        self.setMouseInteraction(False)
        if self.inBrushStroke:
            self.brush.continue_stroke(x, y, e.pressure())
        else:
            self.inBrushStroke = True
            self.brush = paint_engine_obsolete.SimpleBrush(self.layerStack.activeLayer(), self.brush_properties)
            self.brush.start_stroke(x, y, e.pressure())
        e.accept()
        self.update()

    def enterPickerMode(self):
        self.mode = 'picker'
        pmap = QPixmap(3, 3)
        pmap.fill(QColor(0, 0, 0, 0))
        p = QPainter(pmap)
        p.drawEllipse(0, 0, 2, 2)
        p.end()
        self.setCursor(QCursor(pmap))

    def leavePickerMode(self):
        self.mode = None
        self.updateBrushCursor()

    def inPickerMode(self):
        return self.mode == 'picker'

    def keyPressEvent(self, e: QKeyEvent):
        if Qt.AltModifier & e.modifiers():
            self.enterPickerMode()
        elif self.inPickerMode():
            self.leavePickerMode()

    def keyReleaseEvent(self, e: QKeyEvent):
        pass


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


class NewPaintingDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = ui.new_painting_dialog.Ui_Dialog()
        self.ui.setupUi(self)


def main():
    app = QApplication(sys.argv)
    w = NewPaintingDialog()
    w.show()
    app.exec_()


if __name__ == "__main__":
    main()