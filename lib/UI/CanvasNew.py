from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from numpy import arange, sin, pi
from PyQt5.QtCore import QSize, Qt, pyqtSlot, QTimer, pyqtSignal
import logging
from lib.Log import LOGGER

class CanvasNew(FigureCanvas):

    def __init__(self, width=5, height=4):
        self.logger = logging.getLogger(LOGGER)

        self.fig = Figure(figsize=(width, height))
        self.axes = self.fig.add_subplot(111)
        self.compute_initial_figure([0,1], [0,1])
        FigureCanvas.__init__(self, self.fig)
        self.axes.legend(['A simple line'])

    def start_timer(self):
        self.timer.start(1000)

    def compute_initial_figure(self, x, y):
        self.axes.plot(x,y)

    

    @pyqtSlot(float, float, str, str)
    def get_data_point(self, x, y, marker, color):
        self.axes.plot(x,y, marker=marker, color=color)
        self.draw_idle()


    @pyqtSlot()
    def clear_canvas(self):
        self.axes.cla()
