from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QPushButton, QGroupBox
from lib.UI.PumpControl import PumpControl
from lib.UI.ValveControl import ValveControl
from lib.Vosekast import BASE_PUMP, MEASURING_PUMP, MEASURING_TANK_SWITCH, MEASURING_TANK_VALVE

class TabStatus(QWidget):

    def __init__(self):
        super().__init__()
        self.pump_buttons = {}
        self.valve_buttons = {}

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

        pump_base = PumpControl('Pump Base')
        self.pump_buttons[BASE_PUMP] = pump_base
        layout.addWidget(pump_base, 0, 0)

        pump_measuring = PumpControl('Pump Measuring')
        self.pump_buttons[MEASURING_PUMP] = pump_measuring
        layout.addWidget(pump_measuring, 0, 1)

        pumps_group_box.setLayout(layout)
        return pumps_group_box

    def create_valves(self):
        valves_group_box = QGroupBox("Valves")
        layout = QGridLayout()
        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 0)

        valve_measuring = ValveControl('Valve Measuring')
        self.valve_buttons[MEASURING_TANK_VALVE] = valve_measuring
        layout.addWidget(valve_measuring, 0, 0)

        valve_switch = ValveControl('Valve Switch Measuring')
        self.valve_buttons[MEASURING_TANK_SWITCH] = valve_switch
        layout.addWidget(valve_switch, 0, 2)

        valves_group_box.setLayout(layout)
        return valves_group_box

    def create_scale(self):
        scale_box = QGroupBox('Scale')
        return scale_box
