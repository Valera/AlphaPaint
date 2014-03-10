from PyQt5.QtGui import QPixmap, QImage, QPainter
from PyQt5.QtWidgets import QLabel, QApplication

__author__ = 'vfedotov'

def show_qimage(qimage: QImage, scale=1):
    app = QApplication([])
    lbl = QLabel()
    pm = QPixmap(qimage.width() * scale, qimage.height() * scale)
    qp = QPainter(pm)
    qp.scale(scale, scale)
    qp.drawImage(0, 0, qimage)
    qp.end()
    lbl.setPixmap(pm)
    lbl.show()
    exit(app.exec_())
