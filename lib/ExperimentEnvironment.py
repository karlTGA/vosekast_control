import logging
from lib.Log import LOGGER
import time
import matplotlib.pyplot as plt


#from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import pyqtSignal, QObject, QTimer, pyqtSlot

import numpy as np
from numpy import arange, sin, cos, pi, log
import time
from lib.EnumStates import States
from lib.Experiment import Experiment



class ExperimentEnvironment(QObject):

    # signals
    state_changed = pyqtSignal(int, name="ExpEnvStateChanged")
    #send_data_point = pyqtSignal(float, float, name="point")
    new_time = pyqtSignal(int, name="time_exp_env")

    def __init__(self, delta_t, vosekast, main_window, index=0, funcs=['sin', 'cos', 'sqrt', 'log'], update = False):
        super().__init__()

        self.logger = logging.getLogger(LOGGER)
        self.delta_t = delta_t
        self.vosekast = vosekast

        self._main_window = main_window
        self._exp_env_tab = self._main_window.tabs.tabProgramms
        self._start_pause_button = self._exp_env_tab.exp_env_buttons[index]

        # add instance to gui_elements
        self._start_pause_button.control_instance = self

        # Add Experiment
        self.experiment_0 = Experiment(self, [3,6,9], [4,8,12])
        self.experiment_1 = Experiment(self, [1,2,7], [9,6,18])
        self.experiment_2 = Experiment(self, [1,3,8], [7,5,11])
        self.experiments = [self.experiment_0, self.experiment_1, self.experiment_2]

        self.change_state(States.READY.value)


    def change_state(self, new_state):
        self.state = States(new_state)
        self.logger.debug('New State ' + str(new_state))
        self.state_changed.emit(new_state)

    def send_new_time(self):
        self.new_time.emit(0)

    def get_state(self):
        return self.state

    def start_run(self):
        self.logger.debug("Start run {}".format('Hallo'))
        self.logger.debug('Jetzt sollte geplottet werden')

        t = np.linspace(0, self.delta_t, 200)
        y = sin(t)

        self.vosekast._main_window.tabs.tabProgramms.screen.axes.cla()
        self.vosekast._main_window.tabs.tabProgramms.screen.axes.plot(t,y)
        self.vosekast._main_window.tabs.tabProgramms.screen.draw()
        self.change_state(States.RUNNING.value)
        self.timer.start(1000)

    def pause_run(self):
        self.timer.stop()
        self.change_state(States.PAUSE.value)
