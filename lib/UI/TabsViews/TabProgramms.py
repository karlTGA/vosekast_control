from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QPushButton, QGroupBox
from lib.UI.OnOffControl import OnOffControl
from lib.ExperimentEnvironment import ExperimentEnvironment

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

from lib.Vosekast import Vosekast, BASE_PUMP, MEASURING_PUMP, MEASURING_TANK_SWITCH, MEASURING_TANK_VALVE, BASE_TANK, MEASURING_TANK




from lib.UI.CanvasDynamicDefault import CanvasDynamicDefault
from lib.UI.CanvasStatic import CanvasStatic
from lib.UI.CanvasNew import CanvasNew


class TabProgramms(QWidget):

    def __init__(self):
        super().__init__()
        self.exp_env_buttons = {}
        self.initUI()


    def initUI(self):
        self.plot_box = self.create_canvas()
        on_off_boxes = self.create_on_off(3)



        self.windowLayout = QGridLayout()
        #self.windowLayout.setColumnStretch(0, 1)
        #self.windowLayout.setColumnStretch(1, 1)

        self.windowLayout.addWidget(on_off_boxes, 0, 0, 1, 1)
        self.windowLayout.addWidget(self.plot_box, 0, 1, 1, 5)
        self.setLayout(self.windowLayout)

    def create_on_off(self, number):
        out = QGroupBox("Trials")
        layout = QGridLayout()
        layout.setSpacing(10)

        for a in range(number):
            button = OnOffControl('Trial ' + str(a))
            self.exp_env_buttons[a] = button
            layout.addWidget(button, a, 0, 1, 0)

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
