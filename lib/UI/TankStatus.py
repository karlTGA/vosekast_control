from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QProgressBar, QLineEdit
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QSize, Qt, pyqtSlot

import os
from lib.Tank import Tank


class TankStatus(QWidget):

    def __init__(self, name):
        super().__init__()
        self.name = name
        self.fill_state = None
        self.label = None
        self.tank = None
        self.fill_text = None
        self.initUI()

    def initUI(self):
        self.tank = QLabel()
        self.tank.setPixmap(QPixmap(self.get_icon(Tank.UNKNOWN)))

        self.fill_state = QProgressBar()
        self.fill_state.setOrientation(Qt.Vertical)
        self.fill_state.setMinimum(0)
        self.fill_state.setMaximum(100)

        self.fill_text = QLabel()

        layout = QGridLayout()
        layout.addWidget(self.tank, 0, 0, Qt.AlignHCenter)
        layout.addWidget(self.fill_state, 0, 1, Qt.AlignHCenter)
        layout.addWidget(self.fill_text, 0, 2, Qt.AlignCenter)

        self.setLayout(layout)

    def handle_state_change(self, new_state):
        self.fill_state.setValue(new_state*100)
        self.tank.setPixmap(QPixmap(self.get_icon(new_state)))
        self.fill_text.setText("{} %".format(str(new_state*100)))


    @pyqtSlot(float)
    def state_change(self, new_state):
        self.handle_state_change(new_state)

    @staticmethod
    def get_icon(state):
        # search for icon
        path = os.path.dirname(os.path.abspath(__file__))

        if state < Tank.DRAINED:
            icon_path = os.path.join(path, 'icons/tank_icons/tank_sw.png')
        else:
            icon_path = os.path.join(path, 'icons/tank_icons/tank_color.png')

        if not os.path.isfile(icon_path):
            raise NoImageForIconError

        return icon_path


class NoImageForIconError(Exception):
    pass

