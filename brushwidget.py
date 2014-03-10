from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSlider, QApplication, QLabel, QGridLayout, QSizePolicy
import sys

__author__ = 'vfedotov'

class PropertyDescription:
    def __init__(self, name, min, max, default, editorType='slider'):
        self.name = name
        self.min = min
        self.max = max
        self.default = default
        self.editorType = editorType

class BrushWidget(QWidget):
    def __init__(self, propertyList):
        super().__init__()
        self.grid = QGridLayout()
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(0)
        self.editors = {}

        rowInd = 0
        for prop in propertyList:
            nameLabel = QLabel(prop.name)
            self.grid.addWidget(nameLabel, rowInd, 0)
            slider = QSlider(Qt.Horizontal)
            slider.setRange(prop.min, prop.max)
            self.grid.addWidget(slider, rowInd, 1)
            valueLabel = QLabel()
            self.grid.addWidget(valueLabel, rowInd, 2)
            def update(editor):
                return lambda x: editor.setText(str(x))
            slider.valueChanged.connect(update(valueLabel))
            slider.setValue(prop.default)
            self.editors[prop.name] = [nameLabel, slider, valueLabel]
            self.grid.setRowStretch(rowInd, 0)
            rowInd += 1
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.setLayout(self.grid)


def main():
    app = QApplication(sys.argv)
    w = BrushWidget([PropertyDescription('Size', 1, 500, 20), PropertyDescription('Opacity', 0, 255, 255),
                     PropertyDescription('Hardness', 0, 255, 255), PropertyDescription('Spacing', 1, 20, 10)])
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()