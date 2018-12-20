from PyQt5.QtWidgets import QWidget, QGridLayout, QToolButton, QLabel
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, Qt, pyqtSlot
import logging
from lib.Log import LOGGER
from lib.EnumStates import States


class ControlField(QWidget):

    def __init__(self, text, default_state=States.NONE):
        super().__init__()
        self.text = text
        self.state = default_state
        self.button = None
        self.label = None
        self.control_instance = None
        self.logger = logging.getLogger(LOGGER)

        self.initUI()

    def initUI(self):
        self.button = QToolButton()
        self.button.setText(self.text)

        # search for icon
        icon_path = self.get_icon(self.state)

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

    def set_control_instance(self, instance):
        """
        the button should control this instance
        :return:
        """
        self.control_instance = instance

    def handle_click(self):
        if self.control_instance is None:
            self.logger.warning("To the button {} was no pump instance added.".format(self.text))
            return

        self.toggle_control_instance()

    def toggle_control_instance(self):
        pass

    def handle_state_change(self, new_state):
        self.button.setIcon(QIcon(self.get_icon(new_state)))
        self.state = new_state

    @pyqtSlot(int)
    def state_change(self, new_state):
        print('ControlField, Singal income')
        self.handle_state_change(States(new_state))

    @staticmethod
    def get_icon(state):
        return ""


class NoImageForIconError(Exception):
    pass
