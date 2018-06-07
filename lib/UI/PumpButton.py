from PyQt5.QtWidgets import QWidget, QGridLayout, QToolButton, QLabel
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, Qt
import os


class PumpButton(QWidget):

    def __init__(self, label):
        super().__init__()
        self.label = label
        self.initUI()

    def initUI(self):
        button = QToolButton()
        button.setText(self.label)

        # search for icon
        path = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(path, 'icons/pump_icons/pump_color_1.png')

        if not os.path.isfile(icon_path):
            raise NoImageForIconError

        button.setIcon(QIcon(os.path.join(path, 'icons/pump_icons/pump_color_1.png')))
        button.setIconSize(QSize(128, 128))
        button.setStyleSheet("padding: 10px")

        # add event handler
        button.clicked.connect(self.handleButton)

        # build label
        label = QLabel()
        label.setText(self.label)

        # build button with text
        layout = QGridLayout()
        layout.addWidget(button, 0, 0, Qt.AlignHCenter)
        layout.addWidget(label, 1, 0, Qt.AlignCenter)

        self.setLayout(layout)

    def handleButton(self):
        pass


class NoImageForIconError(Exception):
    pass
