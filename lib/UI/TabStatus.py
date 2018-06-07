from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QPushButton, QGroupBox
from lib.UI.PumpButton import PumpButton

class TabStatus(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        pumps_group_box = self.create_pumps()
        valves_group_box = self.create_valves()
        scale_box = self.create_scale()

        windowLayout = QGridLayout()
        windowLayout.addWidget(pumps_group_box, 0, 0, 1, 3)
        windowLayout.addWidget(valves_group_box, 1, 0, 1, 3)
        windowLayout.addWidget(scale_box, 0, 3, 1, 3)

        self.setLayout(windowLayout)

    def create_pumps(self):
        pumps_group_box = QGroupBox("Pumps")
        layout = QGridLayout()
        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 0)

        layout.addWidget(PumpButton('Pump Stock'), 0, 0)
        layout.addWidget(PumpButton('Pump Measuring'), 0, 1)

        pumps_group_box.setLayout(layout)
        return pumps_group_box

    def create_valves(self):
        valves_group_box = QGroupBox("Valves")
        layout = QGridLayout()
        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 0)

        layout.addWidget(QPushButton('Switch Measuring'), 0, 0)
        layout.addWidget(QPushButton('Valve Measuring'), 0, 2)

        valves_group_box.setLayout(layout)
        return valves_group_box

    def create_scale(self):
        scale_box = QGroupBox('Scale')
        return scale_box
