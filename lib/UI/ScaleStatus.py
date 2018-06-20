from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QSize, Qt, pyqtSlot
import os


class ScaleStatus(QWidget):

    def __init__(self, name):
        super().__init__()

        self.state_text = None
        self.value_text = None
        self.scale = None
        self.initUI()

    def initUI(self):
        self.scale = QLabel()
        self.scale.setPixmap(QPixmap(self.get_icon()))
        self.state_text = QLabel()
        self.value_text = QLabel()

        layout = QGridLayout()
        layout.addWidget(self.scale, 0, 0, Qt.AlignVCenter)
        layout.addWidget(self.state_text, 1, 0, Qt.AlignVCenter)
        layout.addWidget(self.value_text, 2, 0, Qt.AlignCenter)

        self.setLayout(layout)


    @staticmethod
    def get_icon():
        # search for icon
        path = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(path, 'icons/scale_icons/scale_color.png')

        if not os.path.isfile(icon_path):
            raise NoImageForIconError

        return icon_path

    def handle_state_change(self, new_state):
        self.state_text.setText(new_state)

    def handle_value_change(self, new_value):
        self.value_text.setText(new_value)

    @pyqtSlot(bool)
    def state_change(self, new_state):
        if new_state:
            self.handle_state_change("Stable")
        else:
            self.handle_state_change("Unstable")

    @pyqtSlot(float)
    def value_change(self, new_value):
        self.handle_value_change(str(round(new_value, 2)) + " kg")

class NoImageForIconError(Exception):
    pass
