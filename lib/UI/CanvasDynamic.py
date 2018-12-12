from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from numpy import arange, sin, pi
from lib.UI.Canvas import Canvas
from PyQt5 import QtCore, QtWidgets
import random
from numpy import arange, sin, cos, pi, sqrt, log
#from CanvasDynamic import CanvasDynamic


class CanvasDynamic(Canvas):
    """A canvas that updates itself every second with a new plot."""

    def __init__(self, funcs=['sin', 'cos', 'root']):
        Canvas.__init__(self)
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_figure)
        timer.start(1000)
        self.time = 0
        self.funcs = funcs

    def compute_initial_figure(self):
        self.axes.plot([0, 1, 2, 3], [1, 2, 0, 4], color = 'k')

    def update_figure(self):
        self.time += 1
        print(self.time)

        t = range(self.time)

        self.axes.cla()
        if 'cos' in self.funcs:
            self.axes.plot(t, cos(t))
        if 'sin' in self.funcs:
            self.axes.plot(t, sin(t))
        if 'sqrt' in self.funcs:
            self.axes.plot(t, sqrt(t))
        if 'log' in self.funcs:
            self.axes.plot(t, log(t))

        #self.axes.set_ylim(-2,2)
        self.draw()
