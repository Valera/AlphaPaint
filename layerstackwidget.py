import sys

from PyQt5.QtCore import QRectF, QVariant, QPointF, Qt
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsItem, QStyleOptionGraphicsItem, \
    QGraphicsSceneMouseEvent, QGraphicsRectItem
from layers import LayerStack


__author__ = 'Valeriy A. Fedotov, valeriy.fedotov@gmail.com'


class LayerItem(QGraphicsItem):
    def __init__(self):
        super().__init__()
        self.setFlag(self.ItemIsMovable, True)
        self.setFlag(self.ItemIsSelectable, True)
        self.setFlag(self.ItemSendsGeometryChanges, True)
        self.setFlag(self.ItemSendsScenePositionChanges, True)
        self.sub0 = QGraphicsRectItem(10, 10, 50, 50, self)
        self.sub1 = QGraphicsRectItem(100, 50, 10, 10, self)
        self.sub2 = QGraphicsRectItem(120, 50, 10, 10, self)
        self.sub3 = QGraphicsRectItem(140, 50, 10, 10, self)

    def boundingRect(self):
        return QRectF(0, 0, 201, 71)

    def paint(self, p: QPainter, s: QStyleOptionGraphicsItem, QWidget_widget=None):
        p.setBrush(QColor("#003366"))
        p.drawRect(0, 0, 200, 70)

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value: QVariant):
        if change == self.ItemPositionHasChanged:
            pos = value
            assert isinstance(pos, QPointF)
            pos.setX(0)
            pos.setY(round(pos.y() / 75) * 75)
            return pos
        if change == self.ItemPositionChange:
            pos = value
            assert isinstance(pos, QPointF)
            self.scene().layerIsMoving(pos.y() - 75 / 2)
            pos.setX(0)
            return pos
        return value

    def mousePressEvent(self, QGraphicsSceneMouseEvent):
        self.setOpacity(0.2)

    def mouseReleaseEvent(self, QGraphicsSceneMouseEvent):
        self.setOpacity(1)

    def reAlign(self):
        self.setY(round(self.y() / 75) * 75)


class LayersStackScene(QGraphicsScene):
    class ActiveRegion(QGraphicsItem):
        def __init__(self):
            super().__init__()
            self.color = QColor(QColor("#0047AB"))

        def boundingRect(self):
            return QRectF(0, 0, 200, 5)

        def paint(self, p: QPainter, QStyleOptionGraphicsItem, QWidget_widget=None):
            p.setBrush(self.color)
            p.drawRect(20, 0, 159, 5)

        def setHighlited(self, boolean):
            if boolean:
                self.color = QColor("#880000")
            else:
                self.color = QColor(QColor("#0047AB"))
            self.update()

    def __init__(self, layerStack):
        super().__init__()
        # self.
        self.layerStack = layerStack
        self.activeRegions = []
        self.layerItems = []
        for ind, layer in enumerate(self.layerStack.layers):
            activeRegion = self.ActiveRegion()
            self.activeRegions.append(activeRegion)
            self.addItem(activeRegion)
            activeRegion.moveBy(0, -5 + 75 * ind)

            item1 = LayerItem()
            self.layerItems.append(item1)
            self.addItem(item1)
            item1.moveBy(0, 75 * ind)
        activeRegion = self.ActiveRegion()
        self.activeRegions.append(activeRegion)
        self.addItem(activeRegion)
        activeRegion.moveBy(0, -5 + 75 * (ind + 1))

    def layerIsMoving(self, y):
        if abs(y + 2 - round((y + 2) / 75) * 75) < 20:
            for ind, ar in enumerate(self.activeRegions):
                if abs(y + 2 - (ind - 1)* 75) < 20:
                    ar.setHighlited(True)
                else:
                    ar.setHighlited(False)
        else:
            for ar in self.activeRegions:
                ar.setHighlited(False)
        if self.views():
            self.views()[0].horizontalScrollBar().setDisabled(True)

    def mouseReleaseEvent(self, e: QGraphicsSceneMouseEvent):
        super().mouseReleaseEvent(e)
        self.selectedItems()[0].reAlign()


def main():
    app = QApplication(sys.argv)
    w = QGraphicsView()
    ls = LayerStack(100, 100)
    ls.add_layer_above()
    ls.add_layer_above()
    w.setScene(LayersStackScene(ls))
    w.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    w.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()