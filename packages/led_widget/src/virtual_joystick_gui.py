#!/usr/bin/env python3
import os
import socket
import sys
import time
from typing import NamedTuple

from PyQt5 import QtCore
from PyQt5.QtCore import QSize, pyqtSignal, Qt
from PyQt5.QtCore import QThread, QTimer
from PyQt5.QtGui import QIcon, QPixmap, QTransform
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QLabel, QMainWindow, QSlider
from pynput.keyboard import Listener

import rospy
from duckietown_msgs.msg import LedPattern

HZ = 30
SCREEN_SIZE = 300
time_to_wait = 10000


class KeyMap(NamedTuple):
    KEY_R: str
    KEY_G: str
    KEY_B: str
    KEY_Y: str
    KEY_W: str
    KEY_Q: str

keys = KeyMap('r', 'g', 'b', 'y', 'w', 'q')


class ROSManager(QThread):

    def __init__(self, parent):
        QThread.__init__(self, parent)
        self._parent = parent
        rospy.init_node('led_widget', anonymous=False)
        self.pub_led_pattern = rospy.Publisher(
            "~led_pattern",
            LedPattern,
            queue_size=1
        )
        self.commands = set()
        self._is_shutdown = False
        self.last_ms = 0

    def shutdown(self):
        self._is_shutdown = True

    def run(self):
        while not self._is_shutdown:
            ms_now = int(round(time.time() * 1000))

            try:
                if ms_now - self.last_ms > time_to_wait:
                    rospy.get_master().getSystemState()
                    self.last_ms = ms_now
            except socket.error:
                print("Error starting main loop in led widget gui")

            msg = LedPattern() # TODO: Init this
            allow_publish = self._parent.inFocus

            # Keyboard events
            if keys.KEY_R in self.commands:
                pass # Set color

            elif keys.KEY_G in self.commands:
                pass

            elif keys.KEY_B in self.commands:
                pass

            elif keys.KEY_Y in self.commands:
                pass

            elif keys.KEY_W in self.commands:
                pass

            elif keys.KEY_Q in self.commands:
                print('Received shutdown request (`Q` button down).')
                self.shutdown()
                self._parent.shutdown()

            if allow_publish:
                self.pub_led_pattern.publish(msg)

            time.sleep(1 / HZ)

    def action(self, commands):
        self.commands = commands


class MyKeyBoardThread(QThread):
    key_board_event = pyqtSignal(object)

    def __init__(self, parent):
        QThread.__init__(self, parent)
        self._parent = parent
        self.listener = None
        self.commands = set()

    def add_listener(self, listener):
        self.key_board_event.connect(listener)

    def on_press(self, key):
        if not self._parent.inFocus:
            return
        key_val = str(key)
        if len(key_val) == 3:
            key_val = key_val[1]
        if key_val in keys:
            self.commands.add(keys[key_val])
        self.key_board_event.emit(self.commands)

    def on_release(self, key):
        if not self._parent.inFocus:
            return
        key_val = str(key)
        if len(key_val) == 3:
            key_val = key_val[1]
        if key_val in keys:
            self.commands.discard(keys[key_val])
        self.key_board_event.emit(self.commands)

    def run(self):
        with Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            self.listener = listener
            self.listener.join()

    def shutdown(self):
        self.listener.stop()
        self.quit()


class MainWindow(QMainWindow):

    def __init__(self, title, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        script_path = os.path.dirname(__file__)
        self.script_path = (script_path + "/") if script_path else ""
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon(self.script_path + '../images/logo.png'))
        self._has_focus = False

        # ros class
        self.ros = ROSManager(self)
        self.ros.start()
        # Keyboard
        self.key_board_event = MyKeyBoardThread(self)
        self.key_board_event.add_listener(self.visual_led_controller)
        self.key_board_event.start()
        # UI LED Controller
        self.widget = Controller(self)
        self.widget.ros_fun.connect(self.visual_led_controller)
        self.resize(self.widget.pixmap.width() + 20, self.widget.pixmap.height())
        self.setFixedSize(self.widget.pixmap.width() + 20, self.widget.pixmap.height())
        self.setCentralWidget(self.widget)
        self.ros_commands = set()
        self.was_added_new_key = False
        self.widget.change_state()
        self.installEventFilter(self)

    def eventFilter(self, object, event):
        if event.type() in [QtCore.QEvent.WindowActivate, QtCore.QEvent.WindowDeactivate, QtCore.QEvent.FocusIn, QtCore.QEvent.FocusOut]:
            self._has_focus = (event.type() in [QtCore.QEvent.WindowActivate, QtCore.QEvent.FocusIn])
            self.widget.change_state()
        # ---
        return False

    @property
    def inFocus(self):
        return self._has_focus

    def visual_led_controller(self, commands):
        active = self.isActiveWindow()
        if active and self.inFocus:
            self.widget.light_d_pad(commands)
            if commands:
                self.ros.action(commands)

    def shutdown(self):
        self.ros.shutdown()
        self.key_board_event.shutdown()
        self.close()


class Controller(QWidget):
    ros_fun = pyqtSignal(set)

    def __init__(self, parent, *args, **kwargs):
        super(Controller, self).__init__(*args, **kwargs)
        self._parent = parent
        # GUI stuff init
        self.label_up = None
        self.label_left = None
        self.label_down = None
        self.label_right = None
        self.label_stop = None
        self.main_label = None
        self.label_publisher = None
        self.pixmap = None
        # state init
        self.state_right = True
        self.state_left = True
        self.state_down = True
        self.state_up = True
        # ---
        script_path = os.path.dirname(__file__)
        self.script_path = (script_path + "/") if script_path else ""
        self.initUI()
        self.command = set()
        self.timer = QTimer()
        self.timer.timeout.connect(self.timer_fun)

    def timer_fun(self):
        self.ros_fun.emit(self.command)

    def on_press_timer(self):
        self.timer.start(int(1000 / HZ))

    def on_release_timer(self):
        self.timer.stop()
        self.command.clear()
        self.ros_fun.emit(set())

    def initUI(self):
        self.main_label = QLabel(self)
        self.pixmap = QPixmap(self.script_path + '../images/d-pad.png')
        self.pixmap = self.pixmap.scaled(SCREEN_SIZE, SCREEN_SIZE, Qt.KeepAspectRatio)
        self.main_label.setPixmap(self.pixmap)
        self.resize(SCREEN_SIZE, SCREEN_SIZE)
        # NOTE: if SCREEN_SIZE changed, need to change funs for buttons
        self.create_up_button()
        self.create_left_button()
        self.create_right_button()
        self.create_down_button()
        self.create_d_pad()
        self.create_slider()

    def create_slider(self):
        self.sld = QSlider(Qt.Vertical, self)
        self.sld.setFocusPolicy(Qt.NoFocus)
        self.sld.setRange(0, 100)
        self.sld.setValue(100)
        self.sld.setPageStep(1)
        self.sld.setGeometry(0, 0, SCREEN_SIZE * 2 + 20, SCREEN_SIZE)
        self.sld.valueChanged.connect(self.changeSlider)

    def changeSlider(self, value) -> int:
        return value

    def light_d_pad(self, commands):
        self.state_left = not (KEY_LEFT in commands)
        self.state_right = not (KEY_RIGHT in commands)
        self.state_up = not (KEY_UP in commands)
        self.state_down = not (KEY_DOWN in commands)
        self.change_state()

    def change_state(self):
        if not e_stop:
            self.label_up.setHidden(self.state_up)
            self.label_down.setHidden(self.state_down)
            self.label_left.setHidden(self.state_left)
            self.label_right.setHidden(self.state_right)
            self.label_stop.setHidden(True)
        else:
            self.label_up.setHidden(True)
            self.label_down.setHidden(True)
            self.label_left.setHidden(True)
            self.label_right.setHidden(True)
            self.label_stop.setHidden(False)
        # ---
        self.label_publisher.setHidden(not self._parent.inFocus)

    def create_d_pad(self):
        self.label_up = QLabel(self)
        self.label_left = QLabel(self)
        self.label_down = QLabel(self)
        self.label_right = QLabel(self)
        self.label_stop = QLabel(self)
        self.label_publisher = QLabel(self)
        img = QPixmap(self.script_path + '../images/d-pad-pressed.png')
        img = img.scaled(SCREEN_SIZE, SCREEN_SIZE, Qt.KeepAspectRatio)
        t = QTransform()
        self.label_up.setPixmap(img)
        t.rotate(90)
        self.label_right.setPixmap(img.transformed(t))
        t.rotate(90)
        self.label_down.setPixmap(img.transformed(t))
        t.rotate(90)
        self.label_left.setPixmap(img.transformed(t))
        # e-stop
        img = QPixmap(self.script_path + '../images/d-e-stop.png')
        img = img.scaled(SCREEN_SIZE, SCREEN_SIZE, Qt.KeepAspectRatio)
        self.label_stop.setPixmap(img)
        # publisher icon
        img = QPixmap(self.script_path + '../images/d-publisher.png')
        img = img.scaled(SCREEN_SIZE, SCREEN_SIZE, Qt.KeepAspectRatio)
        self.label_publisher.setPixmap(img)
        # ---
        self.change_state()

    def create_up_button(self):
        button_up = QPushButton("", self)
        icon = QIcon(self.script_path + '../images/up_button.jpg')
        button_up.setIcon(icon)
        size = 100
        button_up.setIconSize(QSize(size, size))
        button_up.resize(QSize(size - 25, size - 10))
        button_up.move(int(SCREEN_SIZE / 2 - SCREEN_SIZE / 8), 15)
        button_up = self.add_listener_to_button(button_up, {'up'})
        button_up.pressed.connect(lambda: self.change_command({'up'}))

    def change_command(self, cm):
        self.command = cm

    def add_listener_to_button(self, button, command=None):
        if command is None:
            command = {''}

        def fun():
            self.command = command
            self.on_press_timer()

        button.pressed.connect(fun)
        button.released.connect(self.on_release_timer)
        return button


def print_hint():
    print("\n\n\n")
    print("LED Control Widget")
    print("-----------------------------------")
    print("\n")
    print("Press the color blocks to set the color of the LEDs.")
    print("Press the frequency blocks to change the frequency at which the LEDs blink.")
    print("\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise Exception("No hostname specified!")
    else:
        veh_name = sys.argv[1]
    # ---
    print_hint()
    app = QApplication(sys.argv)
    app.setApplicationName(f"{veh_name} - LED Control Widget")
    m = MainWindow(veh_name)
    m.resize(SCREEN_SIZE, SCREEN_SIZE)
    m.show()
    exit_code = app.exec_()
    m.key_board_event.terminate()
    m.key_board_event.wait()
    m.ros.terminate()
    m.ros.wait()
    sys.exit(exit_code)
