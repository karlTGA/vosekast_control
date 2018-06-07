from PyQt5.QtWidgets import QWidget, QGridLayout, QToolButton, QLabel
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtCore import pyqtSlot
from lib.Pump import Pump
import logging
from lib.Log import LOGGER
import os


class PumpButton(QWidget):

    def __init__(self, text):
        super().__init__()
        self.text = text
        self.state = None
        self.button = None
        self.label = None
        self.pump = None
        self.logger = logging.getLogger(LOGGER)

        self.initUI()

    def initUI(self):
        self.button = QToolButton()
        self.button.setText(self.text)

        # search for icon
        icon_path = self.get_icon(Pump.STOPPED)

        self.button.setIcon(QIcon(icon_path))
        self.button.setIconSize(QSize(128, 128))
        self.button.setStyleSheet("padding: 10px")

        # add event handler
        self.button.clicked.connect(self.handle_click)

        # build label
        self.label = QLabel()
        self.label.setText(self.text)

        # build button with text
        layout = QGridLayout()
        layout.addWidget(self.button, 0, 0, Qt.AlignHCenter)
        layout.addWidget(self.label, 1, 0, Qt.AlignCenter)

        self.setLayout(layout)

    def set_pump(self, pump_instance):
        self.pump = pump_instance

    def handle_click(self):
        if self.pump is None:
            self.logger.warning(F"To the button {self.text} was no pump instance added.")
            return

        if self.state == Pump.RUNNING:
            self.pump.stop()
        else:
            self.pump.start()

    @pyqtSlot(int)
    def state_change(self, new_state):
        self.handle_state_change(new_state)

    def handle_state_change(self, new_state):
        self.button.setIcon(QIcon(self.get_icon(new_state)))
        self.state = new_state

    @staticmethod
    def get_icon(state):
        # search for icon
        path = os.path.dirname(os.path.abspath(__file__))

        if state == Pump.RUNNING:
            icon_path = os.path.join(path, 'icons/pump_icons/pump_color_1.png')
        else:
            icon_path = os.path.join(path, 'icons/pump_icons/pump_sw.png')

        if not os.path.isfile(icon_path):
            raise NoImageForIconError

        return icon_path


class NoImageForIconError(Exception):
    pass
