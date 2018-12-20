from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QPushButton, QGroupBox, QComboBox, QMenu, QToolButton, QWidgetAction, QTextBrowser, QMenuBar, QAction
from lib.UI.StartPauseButton import StartPauseButton
from lib.UI.StopButton import StopButton
from lib.ExperimentEnvironment import ExperimentEnvironment

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

from lib.Vosekast import Vosekast, BASE_PUMP, MEASURING_PUMP, MEASURING_TANK_SWITCH, MEASURING_TANK_VALVE, BASE_TANK, MEASURING_TANK


from lib.UI.CanvasNew import CanvasNew


class TabProgramms(QWidget):

    def __init__(self):
        super().__init__()
        self.exp_env_buttons = {}
        self.initUI()
        #self.addTab(QTextEdit(), "Hello")


    def initUI(self):
        self.plot_box = self.create_canvas()
        on_off_boxes = self.create_on_off()
        selection = self.create_selection_box()

        self.windowLayout = QGridLayout()

        self.windowLayout.addWidget(selection, 0, 0, 1, 0.5)
        self.windowLayout.addWidget(on_off_boxes, 1, 0, 1, 1)
        self.windowLayout.addWidget(self.plot_box, 0, 1, 2, 5)

        self.setLayout(self.windowLayout)

    def create_on_off(self):
        out = QGroupBox("Trials")
        layout = QGridLayout()
        layout.setSpacing(10)

        button = StartPauseButton('Start/Pause')
        self.exp_env_buttons[0] = button
        layout.addWidget(button, 0, 0, 1, 0)
        button = StopButton('Stop')
        self.exp_env_buttons[1] = button
        layout.addWidget(button, 1, 0, 1, 0)

        out.setLayout(layout)
        return out

    def create_canvas(self):
        self.screen = CanvasNew(2,2)
        out = QGroupBox("Graphs")
        layout = QGridLayout()
        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 0)
        layout.addWidget(self.screen, 0, 0)
        out.setLayout(layout)
        return out

    def create_selection_box(self):
        out = QGroupBox("Selection")

        layout = QVBoxLayout(self)


        self.myQMenuBar = QMenuBar(self)
        Menu = self.myQMenuBar.addMenu('Monitored Machines')
        Pump_Measurement_Menu = Menu.addMenu('Pump Measurement')
        Pump_Base_Menu = Menu.addMenu('Pump Base')
        Scale_Menu = Menu.addMenu('Scale')
        Valve_1_Menu = Menu.addMenu('Valve 1')
        Valve_2_Menu = Menu.addMenu('Valve 2')

        Pump_Measurement_Menu.addAction('VolumeFlow')
        Pump_Measurement_Menu.addAction('State')

        self.select_experiment = QMenuBar(self)
        Menu_2 = self.select_experiment.addMenu('Choose Experiment')
        Menu_2.addMenu("Experiment 0")
        Menu_2.addMenu("Experiment 1")
        Menu_2.addMenu("Experiment 2")

        layout.addWidget(self.select_experiment)#, 0, 0, 0, 0)
        layout.addWidget(self.myQMenuBar)#, 1, 0, 0, 0)


        out.setLayout(layout)
        return out

"""
    def new_canvas(self, canvas):
        self.plot_box.deleteLater()
        self.canvas = canvas
        self.plot_box = QGroupBox("Graphs")
        layout = QGridLayout()
        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 0)
        layout.addWidget(self.canvas, 0, 0)
        self.plot_box.setLayout(layout)
        self.windowLayout.addWidget(self.plot_box, 0, 1, 2, 5)
"""
