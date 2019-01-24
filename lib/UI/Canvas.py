from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from numpy import arange, sin, pi
from PyQt5.QtCore import QSize, Qt, pyqtSlot, QTimer, pyqtSignal
import logging
from lib.Log import LOGGER
from lib.EnumStates import States

class Canvas(FigureCanvas):
    """ key function of this class is the slot get_new_data_point, which enables
    other classes or functions to send a data point which is going to be plotted.
    All issues concerning the screen in the middle of the third tab can be
    modified in this class
    """

    def __init__(self, width=20, height=16):
        self.logger = logging.getLogger(LOGGER)

        self.fig, (self.ax1_state, self.ax2) = plt.subplots(2, 1, figsize=(width, height))
        self.ax1_weight =  self.ax1_state.twinx()

        self.axes = [self.ax1_state, self.ax1_weight, self.ax2]

        self.fig.subplots_adjust(hspace=0.5, wspace=0.5)
        self.lines = {}
        self.styles = {}
        self.colors = {}
        self.markers = {}
        self.coordinates = {}
        self.visibles = {}

        self.compute_initial_figure([0,1,1,2,2,3,3,4,4,5,5,6,6], [0,0,1,1,3,3,2,2,4,4,0,0,0], 0)
        self.compute_initial_figure([0,1], [0,1], 2)
        FigureCanvas.__init__(self, self.fig)


    def compute_initial_figure(self, x, y, index):
        self.axes[index].plot(x,y)

    @pyqtSlot(float, float, int, str)
    def get_data_point(self, x, y, index, label):
        """ If the key "label" has already an entry in the dicts above, the point
        just gets appended. If not, a new entry is created and we try to link it
        to a Checkbox. The parameter index describes the axes where the point is
        displayed
        """
        linestyles = ['-', '-', '-', '-', '-']
        colors = ['k', 'b', 'g', 'r', 'y']
        markers = ['.', 'x', 'v', '>', 'h']

        if self.lines.get(label) is None:
            i = len(self.lines) % 5
            self.coordinates[label] = [[x],[y]]
            self.styles[label] = linestyles[i]
            self.colors[label] = colors[i]
            self.markers[label] = markers[i]
            self.lines[label], = self.axes[index].plot(x, y, linestyle=self.styles[label] , marker=self.markers[label], color=self.colors[label], label = label)
        else:
            self.coordinates[label][0].append(x)
            self.coordinates[label][1].append(y)
            try:
                visibility = self.checkboxes[label].isChecked()
            except:
                visibility = True
                self.logger.debug("1 No Line could be added")
            self.lines[label].set_visible(False)
            self.lines[label], = self.axes[index].plot(self.coordinates[label][0], self.coordinates[label][1], linestyle=self.styles[label], marker=self.markers[label], color=self.colors[label], label = label, visible = visibility)
            try:
                self.checkboxes[label].add_line(self.lines[label])
            except:
                self.logger.debug("2 No Line could be added")
        plt.legend(self.lines.values(), self.lines.keys(), loc = 2)
        self.draw_idle()


    @pyqtSlot()
    def init_figure_slot(self):
        ylabels = ["State [-]", "Weight [kg]", "Volume Flow [" + r'$\frac{l}{s}$' + ']' ]
        titles = ['State & Weight', '', 'Volume Flow', 'To be added']

        for index, ax in enumerate(self.axes):
            ax.cla()
            ax.set_title(titles[index])
            ax.set_ylabel(ylabels[index])
        for ax in [self.ax1_state, self.ax2]:
            ax.set_xlabel("time [s]")

        for a in self.coordinates.values():
            a[0] = []
            a[1] = []
        self.axes[0].set_yticks([e.value for e in States])
        self.axes[0].set_yticklabels([e.name for e in States])
