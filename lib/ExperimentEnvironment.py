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
        self.A = 0
        self.B = 1
        self.run_time_state = RunTimeState
        self.state = default_state


    def get_state(self):
        return self.run_time_state(self.state)


    def start_run(self):
        self.state = 1
        a = 0
        start_time = time.perf_counter()

        #fig = plt.figure()

        while a < self.delta_t:
            print(self.get_state(), a)
            b = time.perf_counter() - start_time
            if a < 2.5 < b:
                self.A = 1 - self.A
                self.B = 1 - self.B
            a = b
            plt.plot(a, self.A, '.' 'k')
            plt.plot(a, self.B, '.' 'r')
        self.state = 2
        print(self.get_state(), a)
        self.state = 0
        print(self.get_state(), a)
        plt.show()
