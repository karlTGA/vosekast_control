from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QPushButton, QGroupBox
from lib.UI.OnOffControl import OnOffControl
from lib.ExperimentEnvironment import ExperimentEnvironment

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

from lib.Vosekast import Vosekast, BASE_PUMP, MEASURING_PUMP, MEASURING_TANK_SWITCH, MEASURING_TANK_VALVE, BASE_TANK, MEASURING_TANK




from lib.UI.CanvasDynamicDefault import CanvasDynamicDefault
from lib.UI.CanvasStatic import CanvasStatic



class TabProgramms(QWidget):

    def __init__(self):
        super().__init__()
        self.exp_env_buttons = {}
        self.initUI()

    def initUI(self):
        on_off_box_0 = self.create_on_off(0)
        on_off_box_1 = self.create_on_off(1)
        #on_off_box_2 = self.create_on_off(2)
        self.plot_box = self.create_canvas('r')
        self.windowLayout = QGridLayout()
        self.windowLayout.addWidget(on_off_box_0, 0, 0, 1, 1)
        self.windowLayout.addWidget(on_off_box_1, 1, 0, 1, 1)
        self.windowLayout.addWidget(self.plot_box, 0, 1, 2, 5)
        self.setLayout(self.windowLayout)

    def create_on_off(self, index):
        out = QGroupBox("Trials")
        layout = QGridLayout()
        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 0)
        button = OnOffControl('Trial ' + str(index))

        self.exp_env_buttons[index] = button

        layout.addWidget(button, 0, 0, 1, 0)

        out.setLayout(layout)
        return out

    def create_canvas(self, color):
        self.canvas = CanvasDynamicDefault(2,2, color)
        out = QGroupBox("Graphs")
        layout = QGridLayout()
        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 0)
        layout.addWidget(self.canvas, 0, 0)
        out.setLayout(layout)
        return out

    def change_color_of_default_canvas(self, color):
        self.plot_box.deleteLater()
        self.plot_box = self.create_canvas(color)
        self.windowLayout.addWidget(self.plot_box, 0, 1, 2, 5)
        self.setLayout(self.windowLayout)

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
