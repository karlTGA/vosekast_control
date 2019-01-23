from PyQt5.QtCore import QTimer
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from lib.Log import LOGGER
import logging
import threading
from lib.EnumStates import States

class Experiment(QObject):
    # signals
    send_data_point = pyqtSignal(float, float, int, str, name="point")
    clear_canvas_ = pyqtSignal(int, name='Clear')
    state_changed = pyqtSignal(int, name='changed')
    init_figure_signal = pyqtSignal()

    def __init__(self, ExperimentEnvironment, name, course_pump_measuring, course_pump_base, index, default_state = States.READY, legend='off'):
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
        self.state_changed.connect(self.ExpEnv._main_window.tabs.tabProgramms.exp_env_buttons[0].state_change)
        self.state_changed.connect(self.ExpEnv._main_window.tabs.tabProgramms.exp_env_buttons[1].state_change)
        self.init_figure_signal.connect(self.screen.init_figure_slot)
        self.name = name
        self.legend = legend

    def continue_experiment(self):
        self.timer.start(500)
        self.state = States.RUNNING
        self.change_state(self.state)

    def start_experiment(self):
        self.init_figure_signal.emit()
        self.timer.start(500)
        self.state = States.RUNNING
        self.change_state(self.state)



    def execute_experiment(self):
        old = self.time_count
        self.time_count += 0.5
        for time_toggle in self.cpb:
            if old < time_toggle <= self.time_count:
                self.ExpEnv.vosekast.pump_base_tank.toggle()
                #state_pbt = self.ExpEnv.vosekast.pump_base_tank.state
                #self.ExpEnv.vosekast.VosekastStore.dispatch({ 'type': 'UPDATE_PUMP_BASE_TANK', 'body': {"state": state_pbt.value}})

        for time_toggle in self.cpm:
            if old < time_toggle <= self.time_count:
                self.ExpEnv.vosekast.pump_measuring_tank.toggle()
                #state_pmt = self.ExpEnv.vosekast.pump_measuring_tank.state
                #self.ExpEnv.vosekast.VosekastStore.dispatch({ 'type': 'UPDATE_PUMP_MEASURING_TANK', 'body': {"state": state_pmt.value}})

        weight_scale = self.ExpEnv.vosekast.scale.get_stable_value()
        #state = self.ExpEnv.vosekast.VosekastStore.get_state()["Scale"]["state"]
        #self.ExpEnv.vosekast.VosekastStore.dispatch({ 'type': 'UPDATE_SCALE', 'body': {"value": weight_scale, "state": state}})

        t = self.time_count
        store = self.ExpEnv.vosekast.VosekastStore

        states = store.get_state()
        for a in states:
            self.send_new_data_point(t, states[a]["State"], 0, a + " State")
        self.send_new_data_point(t, states["Scale"]["Value"], 1, "Scale Value")

    def pause_experiment(self):
        self.timer.stop()
        self.state = States.PAUSE
        self.change_state(self.state)

    def send_new_data_point(self, x, y, index, legend):
        self.send_data_point.emit(x, y, index, legend)

    def change_state(self, new_state):
        self.state_changed.emit(States(new_state).value)

    @pyqtSlot()
    def stop_experiment(self):
        if self.state != States.READY:
            self.state = States.STOPPED
        self.timer.stop()
        self.change_state(self.state)
        self.time_count = 0
