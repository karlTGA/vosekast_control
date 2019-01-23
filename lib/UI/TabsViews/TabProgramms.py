from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QPushButton, QCheckBox, QGroupBox, QComboBox, QMenu, QToolButton, QWidgetAction, QTextBrowser, QMenuBar, QAction
from lib.UI.StartPauseButton import StartPauseButton
from lib.UI.StopButton import StopButton
from lib.ExperimentEnvironment import ExperimentEnvironment

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

from lib.Vosekast import Vosekast, BASE_PUMP, MEASURING_PUMP, MEASURING_TANK_SWITCH, MEASURING_TANK_VALVE, BASE_TANK, MEASURING_TANK
from functools import partial

from lib.UI.Canvas import Canvas

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from lib.EnumStates import States

class TabProgramms(QWidget):

    stop_experiments = pyqtSignal(name="stop_all_experiments")

    def __init__(self):
        super().__init__()
        self.exp_env_buttons = {}
        self.Store = []
        self.checkboxes = {}
        self.initUI()

    def initUI(self):
        self.plot_box = self.create_canvas()

        on_off_boxes = self.create_on_off()
        selection_experiments = self.create_selection_box_experiments()

        self.windowLayout = QGridLayout()

        self.windowLayout.setColumnStretch(0, 1)
        self.windowLayout.setColumnStretch(1, 5)
        self.windowLayout.setColumnStretch(2, 1)

        self.windowLayout.addWidget(selection_experiments, 0, 0, 1, 1)
        self.windowLayout.addWidget(on_off_boxes, 1, 0, 1, 1)
        self.windowLayout.addWidget(self.plot_box, 0, 1, 2, 1)

        self.setLayout(self.windowLayout)

    def create_checkboxes(self, Store):
        out = QGroupBox("Monitored Values")
        layout = QVBoxLayout(self)

        self.Store = Store
        state = self.Store.get_state()
        machines = state.keys()

        for a in machines:
            sub = QGroupBox(a)
            sub_layout = QVBoxLayout(self)
            sub.setLayout(sub_layout)
            for to_be_monitored in state[a]:
                checkbox = QCheckBox(to_be_monitored)
                sub_layout.addWidget(checkbox)
                checkbox.setChecked(True)
                self.checkboxes[a + ' ' + to_be_monitored] = checkbox

            layout.addWidget(sub)

        out.setLayout(layout)
        self.windowLayout.addWidget(out, 0, 2, 2, 2)
        self.screen.checkboxes = self.checkboxes
        print('TabProgramms', self.checkboxes.keys())

    def create_on_off(self):
        out = QGroupBox("Start Pause Stop")
        layout = QGridLayout()
        layout.setSpacing(10)

        button = StartPauseButton('Start/Pause')
        self.exp_env_buttons[0] = button
        button.button.clicked.connect(self.new_suptitle)
        layout.addWidget(button, 0, 0, 1, 0)
        button = StopButton('Stop')
        self.exp_env_buttons[1] = button
        button.button.clicked.connect(self.new_suptitle)
        layout.addWidget(button, 1, 0, 1, 0)

        out.setLayout(layout)
        return out

    def create_canvas(self):
        self.screen = Canvas(2,2)
        self.screen.fig.suptitle("No Experiment chosen")
        out = QGroupBox("Graphs")
        layout = QGridLayout()
        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 0)
        layout.addWidget(self.screen, 0, 0)
        out.setLayout(layout)
        return out

    def create_selection_box_experiments(self):
        out = QGroupBox("Selection")

        layout = QVBoxLayout(self)

        self.select_experiment = QMenuBar(self)
        self.Menu_exp = self.select_experiment.addMenu('Choose Experiment')

        layout.addWidget(self.select_experiment)
        out.setLayout(layout)
        return out

    def new_suptitle(self):
        self.screen.fig.suptitle(self.actual_experiment.name + " - " + States(self.actual_experiment.state).name)
        self.screen.draw_idle()

    def set_experiments(self, experiments_to_be_added):
        self.experiments = experiments_to_be_added
        self.exp_actions = []
        for index, a in enumerate(self.experiments):
            exp = QAction(a.name, self, checkable=True)
            self.exp_actions.append(exp)
            self.Menu_exp.addAction(exp)
            exp.triggered.connect(partial(self.another_experiment_chosen, index))
            self.stop_experiments.connect(a.stop_experiment)

    def another_experiment_chosen(self, index, newState):
        for index_, a in enumerate(self.exp_actions):
            if a.isChecked() and index != index_:
                a.toggle()
                self.experiments[index_]
        self.actual_experiment = self.experiments[index]
        self.exp_env_buttons[0].control_instance = self.actual_experiment
        self.exp_env_buttons[1].control_instance = self.actual_experiment
        self.stop_all_experiments()
        self.screen.fig.suptitle(self.actual_experiment.name + " - " + States(self.actual_experiment.state).name)
        self.screen.draw_idle()

    def stop_all_experiments(self):
        self.stop_experiments.emit()
