import logging
from lib.Log import LOGGER
import time
import matplotlib.pyplot as plt
from enum import Enum
from PyQt5.QtCore import pyqtSignal, QObject

PAUSE = 0
RUNNING = 1
READY = 2
STOP = 3

class ExperimentEnvironment(QObject):

    # signals
    state_changed = pyqtSignal(int, name="ExpEnvStateChanged")

    def __init__(self, delta_t, vosekast, main_window):
        super().__init__()

        self.logger = logging.getLogger(LOGGER)
        self.delta_t = delta_t
        self.vosekast = vosekast

        self._main_window = main_window
        self._exp_env_tab = self._main_window.tabs.tabProgramms
        self.canvas = self._main_window.tabs.tabProgramms.canvas
        self._start_pause_button = self._exp_env_tab.exp_env_buttons[0]

        # add instance to gui_elements
        self._start_pause_button.control_instance = self
        self.state_changed.connect(self._start_pause_button.state_change)

        self.change_state(READY)

    def change_state(self, new_state):
        self.state = new_state
        self.logger.debug('New State ' + str(new_state))
        self.state_changed.emit(new_state)

    def get_state(self):
        return self.state

    def start_run(self):
        self.logger.debug("Start run {}".format('Hallo'))
        self.change_state(RUNNING)
        tick, base, measure, a = [], [], [], 0
        start_time = time.perf_counter()

        figure, ax = self._exp_env_tab.new_canvas()

        while a < self.delta_t:
            self.logger.info('Status: {}; Zeit: {}'.format(self.get_state(), a))#self.get_state(), a)#, self.vosekast.pump_measuring_tank.state)
            b = time.perf_counter() - start_time
            if a < self.delta_t / 2. < b:
                self.vosekast.pump_measuring_tank.start()
            a = b
            tick.append(a)
            base.append(self.vosekast.pump_base_tank.state)
            measure.append(self.vosekast.pump_measuring_tank.state)

            ax.plot(tick, base)
            ax.plot(tick, measure)
            self.canvas.draw_idle()
            plt.show()



            #self.canvas.draw_idle()

            #plt.draw()

        self.vosekast.pump_measuring_tank.stop()

        self.change_state(STOP)
