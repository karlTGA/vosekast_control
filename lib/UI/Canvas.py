from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from numpy import arange, sin, pi



class Canvas(FigureCanvas):
    def __init__(self, width=5, height=4):

        fig = Figure(figsize=(width, height))
        self.axes = fig.add_subplot(111)
        self.compute_initial_figure()
        FigureCanvas.__init__(self, fig)

    #    FigureCanvas.setSizePolicy(self,
    #                               QtWidgets.QSizePolicy.Expanding,
    #                               QtWidgets.QSizePolicy.Expanding)
        #FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass
