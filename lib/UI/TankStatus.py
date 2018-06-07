from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QProgressBar
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QSize, Qt

import os
from lib.Tank import Tank


class TankStatus(QWidget):

    def __init__(self):
        super().__init__()
        self.fill_state = None
        self.label = None
        self.tank = None
        self.initUI()

    def initUI(self):
        self.tank = QLabel()
        self.tank.setPixmap(QPixmap(self.get_icon(Tank.FILLED)))

        self.fill_state = QProgressBar()
        self.fill_state.setOrientation(Qt.Vertical)

        layout = QGridLayout()
        layout.addWidget(self.tank, 0, 0, Qt.AlignHCenter)
        layout.addWidget(self.fill_state, 0, 1, Qt.AlignHCenter)


        self.setLayout(layout)

    @staticmethod
    def get_icon(state):
        # search for icon
        path = os.path.dirname(os.path.abspath(__file__))

        if state == Tank.UNKNOWN:
            icon_path = os.path.join(path, 'icons/tank_icons/tank_sw.png')
        else:
            icon_path = os.path.join(path, 'icons/tank_icons/tank_color.png')

        if not os.path.isfile(icon_path):
            raise NoImageForIconError

        return icon_path


class NoImageForIconError(Exception):
    pass

