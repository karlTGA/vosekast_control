from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from numpy import arange, sin, pi
from lib.UI.Canvas import Canvas
from PyQt5 import QtCore, QtWidgets
import random



class CanvasDynamicDefault(Canvas):
    """A canvas that updates itself every second with a new plot."""

    def __init__(self, width, height, color):
        Canvas.__init__(self, width, height)
        self.color = color
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_figure)
        timer.start(1000)

    def compute_initial_figure(self):
        self.axes.plot([0, 1, 2, 3], [1, 2, 0, 4], color = 'k')

    def update_figure(self):
        # Build a list of 4 random integers between 0 and 10 (both inclusive)
        l = [random.randint(0, 10) for i in range(4)]

        self.axes.cla()
        self.axes.plot([0, 1, 2, 3], l, color=self.color)
        self.axes.set_ylim(0,10)
        self.draw()
