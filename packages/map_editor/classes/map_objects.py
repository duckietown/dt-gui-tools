from PyQt5 import QtWidgets, QtCore, QtGui


class ImageObject(QtWidgets.QLabel):
    """Base object class"""
    def __init__(self, img_path: str, parent: QtWidgets.QWidget, object_name: str, layer_name: str, size: tuple = (20, 20)):
        super(ImageObject, self).__init__()
        self.init_size = size
        self.scale = 1
        self.yaw = 0
        self.obj_map_pos = (0, 0)
        self.img_path = img_path
        self.name = object_name
        self.layer_name = layer_name
        self.setParent(parent)
        self.pixmap = None
        self.change_image(img_path)
        self.setMouseTracking(True)

    def is_draggable(self) -> bool:
        return False

    def rotate_object(self, angle_clockwise: float) -> None:
        rotate_angle = (angle_clockwise - self.yaw) % 360.0
        self.yaw = angle_clockwise % 360
        if not rotate_angle // 90 % 2 == 0:
            self.setFixedSize(self.pixmap.height(), self.pixmap.width())
        new_transform = QtGui.QTransform()
        new_transform.rotate(rotate_angle)
        self.pixmap = self.pixmap.transformed(new_transform, QtCore.Qt.SmoothTransformation)
        self.setPixmap(self.pixmap)

    def change_image(self, img_path: str) -> None:
        self.yaw = 0
        self.img_path = img_path
        self.pixmap = QtGui.QPixmap(img_path)
        self.set_size_object((self.init_size[0] * self.scale, self.init_size[1] * self.scale))

    def set_size_object(self, new_size: tuple) -> None:
        resize = QtCore.QSize(new_size[0], new_size[1])
        self.pixmap = self.pixmap.scaled(resize)
        self.setFixedSize(new_size[0], new_size[1])
        self.setPixmap(self.pixmap)
        self.show()

    def scale_object(self, scale: float) -> None:
        yaw = self.yaw
        self.scale = scale
        self.change_image(self.img_path)
        self.rotate_object(yaw)

    def move_object(self, new_position: tuple) -> None:
        self.move(QtCore.QPoint(new_position[0], new_position[1]))

    def change_position(self, new_position: tuple) -> None:
        self.move_object(new_position)
        self.pos().setX(new_position[0])
        self.pos().setY(new_position[1])

    def move_in_map(self, new_position: tuple) -> None:
        self.parentWidget().move_obj_on_map(self.name, new_position,
                                            obj_width=self.width(),
                                            obj_height=self.height())

    def rotate_in_map(self, angle_clockwise: float) -> None:
        self.parentWidget().rotate_obj_on_map(self.name, angle_clockwise % 360)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == QtCore.Qt.RightButton:
            self.change_obj()
        self.parentWidget().mousePressEvent((event, (self.pos().x(), self.pos().y())))

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        self.parentWidget().mouseMoveEvent((event, (self.pos().x(), self.pos().y())))

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        self.parentWidget().mouseReleaseEvent(event)

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        self.parentWidget().wheelEvent(event)

    def set_obj_map_pos(self, pos: tuple) -> None:
        self.obj_map_pos = (pos[0], pos[1])

    def delete_object(self) -> None:
        self.deleteLater()

    def delete_from_map(self) -> None:
        self.parentWidget().delete_object(self)
        self.delete_object()

    def change_obj(self) -> None:
        self.parentWidget().change_obj_info(self.layer_name, self.name)


class DraggableImage(ImageObject):
    """Objects draggable class
        working with Qt coordinates
    """

    def __init__(self, img_path: str, parent: QtWidgets.QWidget, object_name: str, layer_name: str, size: tuple = (20, 20)):
        super(DraggableImage, self).__init__(img_path, parent, object_name, layer_name, size)
        self.drag_start_pos = None

    def is_draggable(self) -> bool:
        return True

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == QtCore.Qt.LeftButton:
            self.setCursor(QtCore.Qt.ClosedHandCursor)
            self.drag_start_pos = event.pos()
            self.raise_()
        elif event.button() == QtCore.Qt.RightButton:
            self.change_obj()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if self.drag_start_pos is not None:
            new_pos = self.pos() + event.pos() - self.drag_start_pos
            self.move_object((new_pos.x(), new_pos.y()))

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == QtCore.Qt.LeftButton:
            self.setCursor(QtCore.Qt.ArrowCursor)
            new_pos = self.pos() + event.pos() - self.drag_start_pos
            self.change_position((new_pos.x(), new_pos.y()))
            self.move_in_map((new_pos.x(), new_pos.y()))
            self.drag_start_pos = None
            self.parentWidget().scene_update()


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    win = QtWidgets.QWidget()
    win.mainLayout = QtWidgets.QHBoxLayout()
    win.setLayout(win.mainLayout)
    win.setFixedSize(1000, 1000)
    win.img_list = [
        "../img/objects/watchtowers.png", "../img/objects/watchtowers.png"
    ]
    for img in win.img_list:
        draggable_image = DraggableImage(img, win)
        win.mainLayout.addWidget(draggable_image)
    win.show()
    sys.exit(app.exec_())
