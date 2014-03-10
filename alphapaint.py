from _curses import COLOR_WHITE
from PyQt5.QtCore import Qt
from brushwidget import BrushWidget, PropertyDescription
from colorcircle import ColorCircle

__author__ = 'Valeriy A. Fedotov, valeriy.fedotov@gmail.com'

import sys
from PyQt5.QtWidgets import (QMainWindow, QApplication, QAction, QScrollArea, QScrollBar, QDockWidget)
from painting import PaintWidget, CustomScrollArea


class AlphaPaintWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.createActions()
        self.createMenu()

        self.scrollArea = CustomScrollArea()
        self.setCentralWidget(self.scrollArea)
        self.setWindowTitle("AlphaPaint v0.001")
        self.brushDock = QDockWidget()
        self.brushDock.setWidget(BrushWidget([PropertyDescription('Size', 1, 500, 20),
                                              PropertyDescription('Opacity', 0, 255, 255),
                                              PropertyDescription('Hardness', 0, 255, 255),
                                              PropertyDescription('Spacing', 1, 20, 10)]))
        # self.brushDock.show()
        self.addDockWidget(Qt.LeftDockWidgetArea, self.brushDock)
        self.colorDock = QDockWidget()
        self.colorDockWidget = ColorCircle(0, 0, 0)
        self.colorDock.setWidget(self.colorDockWidget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.colorDock)


        self.resize(800, 500)

    def createActions(self):
        self.newAction = QAction("&New", self, triggered=self.newFile)
        self.newAction.setShortcut("Ctrl+N")
        self.openAction = QAction("Open", self, triggered=self.openFile)
        self.saveAction = QAction("Save", self, triggered=self.saveFile)
        self.saveAsAction = QAction("Save As", self, triggered=self.saveFileAs)
        self.closeAction = QAction("Close", self, triggered=self.close)

        self.undoAction = QAction("Undo", self)  # TODO: add undo and redo
        self.redoAction = QAction("Redo", self)
        self.cutAction = QAction("Cut", self)
        self.copyAction = QAction("Copy", self)
        self.pasteAction = QAction("Paste", self)

        self.helpAction = QAction("Help", self)
        self.aboutAction = QAction("About", self)

    def createMenu(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.newAction)
        self.fileMenu.addAction(self.openAction)
        self.fileMenu.addAction(self.saveAction)
        self.fileMenu.addAction(self.saveAsAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.closeAction)

    def newFile(self):
        self.setBaseSize(500, 500)
        self.painting = PaintWidget(400, 400)  # TODO: New file dialog
        self.scrollArea.setWidget(self.painting)
        # self.setCentralWidget(self.painting)
        self.colorDockWidget.HSVChanged.connect(self.painting.setBrushHSV)

    def openFile(self):
        pass  # TODO: implement open File

    def saveFile(self):
        pass  # TODO: implement save File

    def saveFileAs(self):
        pass  # TODO: implement saveAs File


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = AlphaPaintWindow()
    w.show()
    app.exec_()
    print('hello')
