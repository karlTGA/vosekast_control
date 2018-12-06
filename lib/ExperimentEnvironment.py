import logging
from lib.Log import LOGGER
import time
import matplotlib.pyplot as plt
from enum import Enum



class RunTimeState(Enum):
    Pause = 0
    Running = 1
    Ready = 2


class ExperimentEnvironment():

    def __init__(self, delta_t, vosekast, gui, default_state = 0):
        self.delta_t = delta_t
        self.vosekast = vosekast
        self.gui = gui
        self.state = default_state
        self.run_time_state = RunTimeState
        self.logger = logging.getLogger(LOGGER)


    def get_state(self):
        return self.run_time_state(self.state)


    def start_run(self):
        self.logger.debug("Start run {}".format('Hallo'))
        self.state = 1
        a = 0
        start_time = time.perf_counter()

        while a < self.delta_t:
            self.logger.info('Status: {}; Zeit: {}'.format(self.get_state(), a))#self.get_state(), a)#, self.vosekast.pump_measuring_tank.state)
            b = time.perf_counter() - start_time
            if a < 2.5 < b:
                self.vosekast.pump_measuring_tank.start()
            a = b

            if self.vosekast.pump_measuring_tank.state is None:
                plt.plot(a, 0, 'x' 'g')
            else:
                plt.plot(a, 1, 'x' 'g')

            if self.vosekast.pump_base_tank.state == None:
                plt.plot(a, 0, '+' 'b')
            else:
                plt.plot(a, 1, '+' 'b')
        self.vosekast.pump_measuring_tank.stop()

        self.state = 0
        plt.show()
