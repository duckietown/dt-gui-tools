#!/usr/bin/env python3
import os
import rospy
import socket
import sys
import time

from PyQt5.QtCore import QSize, Qt, QThread
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QSlider, QGridLayout
from typing import Dict, List, Tuple

from duckietown_msgs.msg import LEDPattern
from std_msgs.msg import ColorRGBA


HZ = 30
SCREEN_SIZE = 300
time_to_wait = 10000
color_map: Dict = {"red": [255.0, 0.0, 0.0],
                   "green": [0.0, 255.0, 0.0],
                   "blue": [0.0, 0.0, 255.0],
                   "white": [255.0, 255.0, 255.0]}


class ROSManager(QThread):

    def __init__(self, parent):
        QThread.__init__(self, parent)
        self._parent = parent
        rospy.init_node('led_widget', anonymous=False)
        self.pub_leds = rospy.Publisher(
            "~led_pattern",
            LedPattern,
            queue_size=1
        )
        self._is_shutdown = False
        self.last_ms = 0

    def run(self):
        # Keep our ROS connection alive
        while not self._is_shutdown:
            ms_now = int(round(time.time() * 1000))

            try:
                if ms_now - self.last_ms > time_to_wait:
                    rospy.get_master().getSystemState()
                    self.last_ms = ms_now
            except socket.error:
                print("Error starting main loop in led widget gui")

            time.sleep(1 / HZ)

    def shutdown(self):
        print('Received shutdown request.')
        self._is_shutdown = True


class MainWindow(QMainWindow):

    def __init__(self, title, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # Get path to images
        workdir = os.path.dirname(__file__)
        self.workdir = (workdir + "/") if workdir else ""

        # Set up the window and elements
        self.set_up_interface(title)
        self.layout = QGridLayout()
        self.widget = QWidget()
        self.define_layout()

        # Set up the ros interface
        self.ros_manager = ROSManager(self)
        self.ros_manager.start()

        # Set up the LED message
        self.message: LEDPattern = LEDPattern()
        self.intensity: float = 1.0
        self.color_list: List[ColorRGBA] = ColorRGBA() * 5

    def set_up_interface(self, title: str):
        self.setWindowTitle(title)
        self.setGeometry(100, 100, SCREEN_SIZE, SCREEN_SIZE)
        self.setWindowIcon(QIcon(self.workdir + '../images/logo.png'))

    def define_layout(self):
        # Intensity slider
        self.create_slider()

        # Color buttons
        size = int(SCREEN_SIZE / 3)
        reg = int(SCREEN_SIZE / 10)
        offset = reg*2 + size

        self.create_color_button('red', size, (reg, reg))
        self.create_color_button('green', size, (offset, reg))
        self.create_color_button('blue', size, (reg, offset))
        self.create_color_button('white', size, (offset, offset))

        # TODO (ente): Add frequency buttons

    def create_slider(self):
        sld = QSlider(Qt.Vertical, self)
        sld.setFocusPolicy(Qt.NoFocus)
        sld.setRange(0, 100)
        sld.setValue(100)
        sld.setPageStep(1)
        sld.setGeometry(10, 10, SCREEN_SIZE * 2 - 50, SCREEN_SIZE-20)
        sld.sliderReleased.connect(self.slider_changed)

    def slider_changed(self):
        self.intensity = float(self.sender().value() / 100)

        for rgba in self.color_list:
            rgba.a = self.intensity

        self.message.rgb_vals = self.color_list
        self.ros_manager.pub_leds.publish(self.message)

    def create_color_button(self, color: str, size: int, pos: Tuple[int, int]):
        button = QPushButton("", self)
        button.setObjectName(color)
        button.setGeometry(pos[0], pos[1], size+3, size+3)
        icon = QIcon(self.workdir + f'../images/{color}.png')
        button.setIcon(icon)
        button.setIconSize(1 * QSize(button.width(), button.height()))
        self.setStyleSheet(f'''
                QPushButton {{
                    border: 15px;
                    border-bottom: 4px solid #A6A6A6;
                    border-right: 4px solid #A6A6A6;
                }}
                QPushButton::pressed {{
                    border-bottom: 4px solid black;
                    border-right: 4px solid black;
                }}''')
        button.clicked.connect(self.color_button_clicked)

        return button

    def color_button_clicked(self):
        color = self.sender()

        for rgba in self.color_list:
            rgba.r = color_map[color][0]
            rgba.g = color_map[color][1]
            rgba.b = color_map[color][2]
            rgba.a = self.intensity

        self.message.rgb_vals = self.color_list
        self.ros_manager.pub_leds.publish(self.message)

    def closeEvent(self, event):
        event.accept()
        self.ros_manager.shutdown()
        self.close()


if __name__ == '__main__':
    # Requires a vehicle to connect to
    if len(sys.argv) < 2:
        raise Exception("No hostname specified!")
    else:
        veh_name = sys.argv[1]

    # Run the app window
    app = QApplication(sys.argv)
    app.setApplicationName(f"{veh_name} - LED Control Widget")
    m = MainWindow(veh_name)
    m.show()

    # On exit event
    m.ros_manager.terminate()
    m.ros_manager.wait()
    sys.exit(app.exec_())
