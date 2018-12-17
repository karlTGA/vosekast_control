from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from numpy import arange, sin, pi
from PyQt5.QtCore import QSize, Qt, pyqtSlot, QTimer, pyqtSignal
import logging
from lib.Log import LOGGER

class CanvasNew(FigureCanvas):
    get_data = pyqtSignal(int, int, name = 'hallo')

    def __init__(self, width=5, height=4):
        self.logger = logging.getLogger(LOGGER)

        fig = Figure(figsize=(width, height))
        self.axes = fig.add_subplot(111)
        self.compute_initial_figure([0,1], [0,1])
        FigureCanvas.__init__(self, fig)
        #self.timer = QTimer(self)
        #self.timer.timeout.connect(self.get_data.emit)


    def start_timer(self):
        self.timer.start(1000)

    def compute_initial_figure(self, x, y):
        self.axes.plot(x,y)

    @pyqtSlot(float, float)
    def new_data_point(self, x, y):
        self.logger.debug('Got new point')
        self.axes.plot(x,y, 'x' 'k')
        self.draw_idle()

    def tick(self):
        print('tick')
