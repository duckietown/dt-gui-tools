#!/usr/bin/env python3

from PyQt5.QtCore import QSize, pyqtSignal, Qt
from PyQt5.QtCore import QThread, QTimer
from PyQt5.QtGui import QImage, QPalette, QBrush, QIcon, QPixmap, QKeyEvent, QTransform
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QLabel, QMainWindow, QVBoxLayout
from pynput.keyboard import Listener
from duckietown_msgs.msg import BoolStamped
from sensor_msgs.msg import Joy
from time import sleep
import socket
import rospy
import time
import sys
import os

HZ = 30
SCREEN_SIZE = 300
KEY_LEFT = 'left'
KEY_RIGHT = 'right'
KEY_UP = 'up'
KEY_DOWN = 'down'
KEY_A = 'a'
KEY_Q = 'q'
KEY_S = 's'
KEY_I = 'i'
KEY_E = 'e'
KEY_P = 'p'

Keys = {
    'Key.up': KEY_UP,
    'Key.down': KEY_DOWN,
    'Key.left': KEY_LEFT,
    'Key.right': KEY_RIGHT,
    KEY_A: KEY_A,
    KEY_Q: KEY_Q,
    KEY_S: KEY_S,
    KEY_I: KEY_I,
    KEY_E: KEY_E,
    KEY_P: KEY_P
}

speed_tang = 1.0
speed_norm = 1.0
time_to_wait = 10000
estop_deadzone_secs = 0.5
e_stop = False
commands = set()


class ROSManager(QThread):

    def __init__(self, parent):
        QThread.__init__(self, parent)
        rospy.init_node('virtual_joy', anonymous=False)
        self.sub_estop = rospy.Subscriber("~emergency_stop", BoolStamped, self.cbEStop, queue_size=1)
        self.pub_joystick = rospy.Publisher("~joy", Joy, queue_size=1)
        self.pub_int = rospy.Publisher("~intersection_go", BoolStamped, queue_size=1)
        self.commands = set()
        self.estop_last_time = time.time()
        self.last_ms = 0
        self.emergency_stop = False

    def cbEStop(self, estop_msg):
        """
        Callback that process the received :obj:`BoolStamped` messages.

        Args:
            estop_msg (:obj:`BoolStamped`): the emergency_stop message to process.
        """
        self.emergency_stop = estop_msg.data
        if self.emergency_stop:
            global e_stop
            e_stop = self.emergency_stop

    def run(self):
        veh_standing = True

        while True:
            ms_now = int(round(time.time() * 1000))

            try:
                if ms_now - self.last_ms > time_to_wait:
                    rospy.get_master().getSystemState()
                    self.last_ms = ms_now
            except socket.error:
                print("Error starting main loop in virtual joystick gui")

            msg = self.get_raw_message()
            force_joy_publish = False

            # Arrows events
            if KEY_LEFT in self.commands:
                msg.axes[3] += speed_norm

            if KEY_RIGHT in self.commands:
                msg.axes[3] -= speed_norm

            if KEY_UP in self.commands:
                msg.axes[1] += speed_tang

            if KEY_DOWN in self.commands:
                msg.axes[1] -= speed_tang

            if KEY_A in self.commands:
                msg.buttons[7] = 1

            if KEY_S in self.commands:
                msg.buttons[6] = 1

            if KEY_I in self.commands:
                msg.buttons[3] = 1

            if KEY_P in self.commands:
                msg_int = BoolStamped()
                msg_int.data = True
                self.pub_int.publish(msg_int)

            if KEY_E in self.commands and (time.time() - self.estop_last_time > estop_deadzone_secs):
                msg.buttons[3] = 1
                self.estop_last_time = time.time()
                force_joy_publish = True

            if KEY_Q in self.commands:
                sys.exit(0)

            stands = (sum(map(abs, msg.axes)) == 0 and sum(map(abs, msg.buttons)) == 0)
            if not stands:
                veh_standing = False

            if (not veh_standing) or force_joy_publish:
                self.pub_joystick.publish(msg)

            if stands:
                veh_standing = True

            sleep(1 / HZ)

    def action(self, commands):
        self.commands = commands

    @staticmethod
    def get_raw_message():
        return Joy(
            axes=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            buttons=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        )


class MyKeyBoardThread(QThread):
    key_board_event = pyqtSignal(object)

    def __init__(self, parent):
        QThread.__init__(self, parent)

    def add_listener(self, listener):
        self.key_board_event.connect(listener)

    def on_press(self, key):
        key_val = str(key)
        if len(key_val) == 3:
            key_val = key_val[1]
        if key_val in Keys.keys():
            commands.add(Keys[key_val])
        self.key_board_event.emit(commands)

    def on_release(self, key):
        key_val = str(key)
        if len(key_val) == 3:
            key_val = key_val[1]
        if key_val in Keys.keys():
            commands.remove(Keys[key_val])
        self.key_board_event.emit(commands)

    def run(self):
        with Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            self.listener = listener
            self.listener.join()

    def terminate(self):
        self.listener.stop()


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle(sys.argv[1])

        # ros class
        self.ros = ROSManager(self)
        self.ros.start()
        # Key board
        self.key_board_event = MyKeyBoardThread(self)
        self.key_board_event.add_listener(self.ros_wrapper)
        self.key_board_event.add_listener(self.visual_joystick)
        self.key_board_event.start()
        # UI JOYSTICK
        self.widget = Joystick()
        self.widget.ros_fun.connect(self.ros_wrapper)
        self.widget.ros_fun.connect(self.visual_joystick)
        self.resize(self.widget.pixmap.width(), self.widget.pixmap.height())
        self.setFixedSize(self.widget.pixmap.width(), self.widget.pixmap.height())
        ####
        self.setCentralWidget(self.widget)
        self.ros_commands = set()
        self.was_added_new_key = False

    def ros_wrapper(self, commands):
        if self.isActiveWindow() and commands:
            self.ros.action(commands)

    def visual_joystick(self, commands):
        if self.isActiveWindow():
            self.widget.light_d_pad(commands)


class Joystick(QWidget):
    ros_fun = pyqtSignal(set)

    def __init__(self, *args, **kwargs):
        super(Joystick, self).__init__(*args, **kwargs)
        self.state_right = True
        self.state_left = True
        self.state_down = True
        self.state_up = True
        script_path = os.path.dirname(__file__)
        self.script_path = (script_path + "/") if script_path else ""
        self.initUI()
        self.setFocusPolicy(Qt.StrongFocus)
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
        label = QLabel(self)
        self.pixmap = QPixmap(self.script_path + '../images/d-pad.png')
        self.pixmap = self.pixmap.scaled(SCREEN_SIZE, SCREEN_SIZE, Qt.KeepAspectRatio)
        label.setPixmap(self.pixmap)
        self.resize(SCREEN_SIZE, SCREEN_SIZE)
        # NOTE: if SCREEN_SIZE changed, need to change funs for buttons
        self.create_up_button()
        self.create_left_button()
        self.create_right_button()
        self.create_down_button()
        self.create_d_pad()

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

    def create_d_pad(self):
        self.label_up = QLabel(self)
        self.label_left = QLabel(self)
        self.label_down = QLabel(self)
        self.label_right = QLabel(self)
        self.label_stop = QLabel(self)
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
        img = QPixmap(self.script_path + '../images/d-e-stop.png')
        img = img.scaled(SCREEN_SIZE, SCREEN_SIZE, Qt.KeepAspectRatio)
        self.label_stop.setPixmap(img)
        self.change_state()

    def create_up_button(self):
        button_up = QPushButton("", self)
        icon = QIcon(self.script_path + '../images/up_button.jpg')
        button_up.setIcon(icon)
        size = 100
        button_up.setIconSize(QSize(size, size))
        button_up.resize(QSize(size - 25, size - 10))
        button_up.move(int(SCREEN_SIZE / 2 - SCREEN_SIZE/8), 15)
        button_up = self.add_listener_to_button(button_up, {'up'})
        button_up.pressed.connect(lambda: self.change_command({'up'}))

    def change_command(self, cm):
        self.command = cm

    def add_listener_to_button(self, button, command={''}):
        def fun():
            self.command = command
            self.on_press_timer()

        button.pressed.connect(fun)
        button.released.connect(self.on_release_timer)
        return button

    def create_left_button(self):
        button = QPushButton("", self)
        icon = QIcon(self.script_path + '../images/left_button.jpg')
        button.setIcon(icon)
        size = 120
        button.setIconSize(QSize(size, size))
        button.resize(QSize(size - 25, size - 25))
        button.move(10, int(SCREEN_SIZE / 2 - size/2 + 25/2))
        button = self.add_listener_to_button(button, {'left'})
        button.pressed.connect(lambda: self.change_command({'left'}))

    def create_right_button(self):
        button = QPushButton("", self)
        icon = QIcon(self.script_path + '../images/right_button.jpg')
        button.setIcon(icon)
        size = 120
        button.setIconSize(QSize(size, size))
        button.resize(QSize(size - 25, size - 25))
        button.move(int(SCREEN_SIZE / 2 + size/2 - 25/2), int(SCREEN_SIZE / 2 - 47))
        button = self.add_listener_to_button(button, {'right'})
        button.pressed.connect(lambda: self.change_command({'right'}))

    def create_down_button(self):
        button = QPushButton("", self)
        icon = QIcon(self.script_path + '../images/down_button.jpg')
        button.setIcon(icon)
        size = 120
        button.setIconSize(QSize(size, size))
        button.resize(QSize(size - 25, size - 25))
        button.move(int(SCREEN_SIZE / 2 - size/2 + 13), int(SCREEN_SIZE / 2 + 47))
        button = self.add_listener_to_button(button, {'down'})
        button.pressed.connect(lambda: self.change_command({'down'}))


def print_hint():
    print("\n\n\n")
    print("Virtual Joystick for your Duckiebot")
    print("-----------------------------------")
    print("\n")
    print("[ARROW_KEYS]:    Use them to steer your Duckiebot")
    print("         [q]:    Quit the program")
    print("         [a]:    Start lane-following a.k.a. autopilot")
    print("         [s]:    Stop lane-following")
    print("         [i]:    Toggle anti-instagram")
    print("         [e]:    Toggle emergency stop")
    print("\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise Exception("No hostname specified!")
    else:
        veh_name = sys.argv[1]
    # ---
    print_hint()
    app = QApplication(sys.argv)
    m = MainWindow()
    m.resize(SCREEN_SIZE, SCREEN_SIZE)
    m.show()
    exit_code = app.exec_()
    m.key_board_event.terminate()
    m.key_board_event.wait()
    m.ros.terminate()
    m.ros.wait()
    sys.exit(exit_code)

