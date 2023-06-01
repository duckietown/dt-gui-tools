from PyQt5 import QtWidgets, QtCore, QtGui
from painter import Painter


class ImageObject(QtWidgets.QLabel):
    """Base object class"""
    def __init__(self, img_path: str, parent: QtWidgets.QWidget, object_name: str, layer_name: str, size: tuple = (20, 20)):
        super(ImageObject, self).__init__()
        self.init_size = size
        self.scale = 1
        self.yaw = 0
        self.img_path = img_path
        self.name = object_name
        self.layer_name = layer_name
        self.is_select = False
        self.is_to_png = False
        self.pixmap = None
        self.setParent(parent)
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
        self.pixmap = self.pixmap.transformed(new_transform)
        self.setPixmap(self.pixmap)

    def change_image(self, img_path: str) -> None:
        self.yaw = 0
        self.img_path = img_path
        self.pixmap = QtGui.QPixmap(img_path)
        self.set_size_object((self.init_size[0] * self.scale, self.init_size[1] * self.scale))

    def set_size_object(self, new_size: tuple) -> None:
        resize = QtCore.QSize(new_size[0], new_size[1])
        if self.is_to_png:
            self.pixmap = self.pixmap.scaled(resize,
                                             transformMode=QtCore.Qt.SmoothTransformation)
        else:
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

    def delete_object(self) -> None:
        self.deleteLater()

    def delete_from_map(self) -> None:
        self.parentWidget().delete_object(self)
        self.delete_object()

    def change_obj(self) -> None:
        self.parentWidget().change_obj_info(self.layer_name, self.name)

    def set_is_to_png(self, val: bool) -> None:
        self.is_to_png = val


class DraggableImage(ImageObject):
    """Objects draggable class
        working with Qt coordinates
    """

    def __init__(self, img_path: str, parent: QtWidgets.QWidget, object_name: str, layer_name: str, size: tuple = (20, 20)):
        super(DraggableImage, self).__init__(img_path, parent, object_name, layer_name, size)
        self.drag_start_pos = None
        self.pose_before_drag = None

    def is_draggable(self) -> bool:
        return True

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == QtCore.Qt.LeftButton:
            self.setCursor(QtCore.Qt.ClosedHandCursor)
            self.drag_start_pos = event.pos()
            self.pose_before_drag = self.pos()
            self.raise_()
            self.is_select = True
        elif event.button() == QtCore.Qt.RightButton:
            self.change_obj()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if self.drag_start_pos is not None:
            new_pos = self.pos() + event.pos() - self.drag_start_pos
            diff_x = new_pos.x() - self.pos().x()
            diff_y = new_pos.y() - self.pos().y()
            if diff_x or diff_y:
                self.parentWidget().move_selected_objects(diff_x, diff_y)
            self.move_object((new_pos.x(), new_pos.y()))

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == QtCore.Qt.LeftButton:
            self.setCursor(QtCore.Qt.ArrowCursor)
            new_pos = self.pos() + event.pos() - self.drag_start_pos
            if self.pose_before_drag.x() != new_pos.x() or self.pose_before_drag.y() != new_pos.y():
                self.change_position((new_pos.x(), new_pos.y()))
                self.parent().move_selected_objects_on_map(self.pose_before_drag - new_pos)
            self.drag_start_pos = None
            self.parentWidget().scene_update()

    def paintEvent(self, QPaintEvent) -> None:
        if self.is_select:
            Painter.draw_border(self)
        else:
            painter = QtGui.QPainter(self)
            painter.drawPixmap(self.rect(), self.pixmap)
