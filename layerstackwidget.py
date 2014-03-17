import sys

from PyQt5.QtCore import QRectF, QVariant, QPointF
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsItem, QStyleOptionGraphicsItem, \
    QGraphicsSceneMouseEvent, QGraphicsRectItem


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


    def __init__(self):
        super().__init__()
        item1 = LayerItem()
        self.addItem(item1)
        item2 = LayerItem()
        self.addItem(item2)
        self.activeRegion = activeRegion = self.ActiveRegion()
        self.addItem(activeRegion)
        activeRegion.moveBy(0, 70)
        item2.moveBy(0, 75)

    def layerIsMoving(self, y):
        if abs(y - round((y / 73)) * 73) < 20:
            self.activeRegion.setHighlited(True)
        else:
            self.activeRegion.setHighlited(False)

    def mouseReleaseEvent(self, e: QGraphicsSceneMouseEvent):
        super().mouseReleaseEvent(e)
        self.selectedItems()[0].reAlign()


def main():
    app = QApplication(sys.argv)
    w = QGraphicsView()
    w.setScene(LayersStackScene())
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()