from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QPushButton, QGroupBox
from lib.UI.OnOffControl import OnOffControl

from lib.Vosekast import BASE_PUMP, MEASURING_PUMP, MEASURING_TANK_SWITCH, MEASURING_TANK_VALVE, BASE_TANK, MEASURING_TANK

class TabProgramms(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        on_off_box_1 = self.create_on_off()
        on_off_box_2 = self.create_on_off()
        on_off_box_3 = self.create_on_off()
        windowLayout = QGridLayout()
        windowLayout.addWidget(on_off_box_1, 1, 5, 1, 3)
        windowLayout.addWidget(on_off_box_2, 0, 1, 1, 0)
        windowLayout.addWidget(on_off_box_3, 0, 1, 1, 1)
        self.setLayout(windowLayout)

    def create_on_off(self):
        on_off_box = QGroupBox("On/Off")

        layout = QGridLayout()
        layout.setColumnStretch(0.1, 0)
        #layout.setColumnStretch(2, 0)

        on_off = OnOffControl('On///Off')
        layout.addWidget(on_off, 0, 0)

        on_off_box.setLayout(layout)
        return on_off_box
