from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QPushButton, QGroupBox
from lib.UI.OnOffControl import OnOffControl
from lib.ExperimentEnvironment import ExperimentEnvironment

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

from lib.Vosekast import Vosekast, BASE_PUMP, MEASURING_PUMP, MEASURING_TANK_SWITCH, MEASURING_TANK_VALVE, BASE_TANK, MEASURING_TANK

from lib.UI.TabsViews.my_static_plot import MyMplCanvas, MyStaticMplCanvas

"""
 l = QtWidgets.QVBoxLayout(self.main_widget)
        sc = MyStaticMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        dc = MyDynamicMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        l.addWidget(sc)
        l.addWidget(dc)
"""




class TabProgramms(QWidget):

    def __init__(self):
        super().__init__()
        self.exp_env_buttons = {}
        self.fig, axes = plt.subplots(2,1)
        self.canvas = FigureCanvas(self.fig)
        self.initUI()

    def initUI(self):

        on_off_box_0 = self.create_on_off(0)
        on_off_box_1 = self.create_on_off(1)
        on_off_box_2 = self.create_on_off(2)


        self.plot_box = self.create_plot(self.fig)

        self.windowLayout = QGridLayout()

        self.windowLayout.addWidget(on_off_box_0, 0, 0, 1, 1)
        self.windowLayout.addWidget(on_off_box_1, 1, 0, 1, 1)
        self.windowLayout.addWidget(on_off_box_2, 2, 0, 1, 1)
        self.windowLayout.addWidget(self.plot_box, 0, 1, 3, 5)

        self.setLayout(self.windowLayout)


    def create_on_off(self, index):
        out = QGroupBox("Trials")
        layout = QGridLayout()
        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 0)
        button = OnOffControl('Trial 1')

        self.exp_env_buttons[index] = button

        layout.addWidget(button, 0, 0, 3, 0)

        out.setLayout(layout)
        return out

    def create_plot(self, figure):
        out = QGroupBox("Graphs")
        layout = QGridLayout()
        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 0)

        layout.addWidget(FigureCanvas(figure), 0, 0)
        out.setLayout(layout)
        return out

    def new_canvas(self):
        self.plot_box.deleteLater()
        layout = QGridLayout()
        new_figure, ax = plt.subplots(1,1)
        self.canvas = FigureCanvas(new_figure)
        self.plot_box = self.create_plot(new_figure)
        self.windowLayout.addWidget(self.plot_box, 0, 1, 3, 5)
        self.setLayout(self.windowLayout)
        return new_figure, ax
