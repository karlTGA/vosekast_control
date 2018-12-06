from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QPushButton, QGroupBox
from lib.UI.OnOffControl import OnOffControl
from lib.ExperimentEnvironment import ExperimentEnvironment

from lib.Vosekast import Vosekast, BASE_PUMP, MEASURING_PUMP, MEASURING_TANK_SWITCH, MEASURING_TANK_VALVE, BASE_TANK, MEASURING_TANK





class TabProgramms(QWidget):

    def __init__(self):
        super().__init__()
        self.exp_env_buttons = {}
        self.initUI()
        print(self.children())




    def initUI(self):

        on_off_box_0 = self.create_on_off(0)
        on_off_box_1 = self.create_on_off(1)
        on_off_box_2 = self.create_on_off(2)
        on_off_box_3 = self.create_on_off(3)
        on_off_box_4 = self.create_on_off(4)
        on_off_box_5 = self.create_on_off(5)
        windowLayout = QGridLayout()
        windowLayout.addWidget(on_off_box_0, 0, 0, 1, 1)
        windowLayout.addWidget(on_off_box_1, 0, 1, 1, 1)
        windowLayout.addWidget(on_off_box_2, 0, 2, 1, 1)
        windowLayout.addWidget(on_off_box_3, 1, 0, 1, 1)
        windowLayout.addWidget(on_off_box_4, 1, 1, 1, 1)
        windowLayout.addWidget(on_off_box_5, 1, 2, 1, 1)

        self.setLayout(windowLayout)


    def create_on_off(self, index):
        on_off_box = QGroupBox("On/Off")
        layout = QGridLayout()
        on_off = OnOffControl('Trial ' + str(index))
        self.exp_env_buttons[index] = on_off
        #print(self.exp_env_buttons[index])
        layout.addWidget(on_off, 0, 0)
        on_off_box.setLayout(layout)
        return on_off_box
