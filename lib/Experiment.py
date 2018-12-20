from PyQt5.QtCore import QTimer
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from lib.Log import LOGGER
import logging
import threading
from lib.EnumStates import States

class Experiment(QObject):
    # signals
    send_data_point = pyqtSignal(float, float, str, str, name="point")
    clear_canvas_ = pyqtSignal(name='Clear')
    state_changed = pyqtSignal(int, name='changed')

    def __init__(self, ExperimentEnvironment, course_pump_measuring, course_pump_base, index, default_state = States.NONE, legend='off'):
        super().__init__()
        self.logger = logging.getLogger(LOGGER)
        self.ExpEnv = ExperimentEnvironment
        self.cpm = course_pump_measuring
        self.cpb = course_pump_base
        self.index = index
        self.screen = self.ExpEnv._exp_env_tab.screen
        self.timer = QTimer()
        self.timer.timeout.connect(self.execute_experiment)
        self.time_count = 0
        self.state = default_state
        self.send_data_point.connect(self.screen.get_data_point)
        self.clear_canvas_.connect(self.screen.clear_canvas)
        self.state_changed.connect(self.ExpEnv._main_window.tabs.tabProgramms.exp_env_buttons[0].state_change)
        self.state_changed.connect(self.ExpEnv._main_window.tabs.tabProgramms.exp_env_buttons[1].state_change)

        self.legend = legend

    def continue_experiment(self):
        self.timer.start(500)
        self.state = States.RUNNING
        self.change_state(self.state)

    def start_experiment(self):
        self.clear_canvas()
        x = self.time_count
        y = self.ExpEnv.vosekast.pump_base_tank.state.value
        self.send_new_data_point(x, y, 'x', 'r')
        y = self.ExpEnv.vosekast.pump_measuring_tank.state.value
        self.send_new_data_point(x, y, '+', 'g')
        self.screen.axes.legend(['Pump Base Tank', 'Pump Measuring Tank'])
        self.timer.start(500)
        self.state = States.RUNNING

        self.change_state(self.state)

    def execute_experiment(self):
        old = self.time_count
        self.time_count += 0.5
        for time_toggle in self.cpb:
            if old < time_toggle <= self.time_count:
                self.ExpEnv.vosekast.pump_base_tank.toggle()
                print('in the loop')
        x = self.time_count
        y = self.ExpEnv.vosekast.pump_base_tank.state.value
        self.send_new_data_point(x, y, 'x', 'r')

        for time_toggle in self.cpm:
            if old < time_toggle <= self.time_count:
                self.ExpEnv.vosekast.pump_measuring_tank.toggle()
                print('in the loop')
        x = self.time_count
        y = self.ExpEnv.vosekast.pump_measuring_tank.state.value
        self.send_new_data_point(x, y, '+', 'g')

    def pause_experiment(self):
        self.timer.stop()
        self.state = States.PAUSE
        self.change_state(self.state)

    def stop_experiment(self):
        self.timer.stop()
        self.state = States.STOPPED
        self.change_state(self.state)
        self.time_count = 0

    def clear_canvas(self):
        self.clear_canvas_.emit()

    def send_new_data_point(self, x, y, marker, color):
        self.send_data_point.emit(x, y, marker, color)

    def change_state(self, new_state):
        self.state_changed.emit(States(new_state).value)
