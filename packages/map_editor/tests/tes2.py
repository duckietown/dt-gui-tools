from PyQt5 import QtWidgets, QtCore, QtGui

class DraggableImage(QtWidgets.QLabel):
    def __init__(self, imgPath=None, parent=None):
        super(DraggableImage, self).__init__()
        self.setParent(parent)
        pixel_map = QtGui.QPixmap(imgPath)
        self.setFixedSize(pixel_map.width(), pixel_map.height())
        self.setPixmap(pixel_map)
        self.drag_start_pos = None

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.setCursor(QtCore.Qt.ClosedHandCursor)
            # This will give us the start position when a drag is triggered
            self.drag_start_pos = event.pos()
            self.raise_()
        super(DraggableImage, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.drag_start_pos is not None:
            # While left button is clicked the widget will move along with the mouse
            self.move(self.pos() + event.pos() - self.drag_start_pos)
        super(DraggableImage, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.setCursor(QtCore.Qt.ArrowCursor)
        self.pos().setX((self.pos() + event.pos() - self.drag_start_pos).x())
        self.pos().setY((self.pos() + event.pos() - self.drag_start_pos).y())
        self.drag_start_pos = None
        super(DraggableImage, self).mouseReleaseEvent(event)


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.mainLayout = QtWidgets.QHBoxLayout()
        self.setLayout(self.mainLayout)
        self.setFixedSize(1000, 1000)
        self._imgList = [
            "watchtower.png", "watchtower.png"
        ]

        for img in self._imgList:
            draggableImage = DraggableImage(imgPath=img, parent=self)
            self.mainLayout.addWidget(draggableImage)


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())