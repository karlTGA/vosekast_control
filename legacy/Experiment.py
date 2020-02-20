#from PyQt5.QtCore import QTimer
#from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from lib.Log import LOGGER
import logging
import threading
from lib.EnumStates import States
from lib.utils.Msg import StatusMessage


class Experiment():
    # signals
    #send_data_point = pyqtSignal(float, float, int, str, name="point")
    #state_changed = pyqtSignal(int, name="changed")
    #init_figure_signal = pyqtSignal()

    def __init__(
        self,
        ExperimentEnvironment,
        name,
        course_pump_measuring,
        course_pump_constant,
        index,
        vosekast,
        default_state=States.READY,
        legend="off",
        
    ):

        super().__init__()
        self.logger = logging.getLogger(LOGGER)
        self.ExpEnv = ExperimentEnvironment
        self.course_pump_measuring = course_pump_measuring
        self.course_pump_constant = course_pump_constant
        self.index = index
        self.vosekast = vosekast
        self.name = name
        #self.screen = self.ExpEnv._exp_env_tab.screen
        self.state = default_state

        self.mqtt = self.vosekast.mqtt_client

        #self.timer = QTimer()
        #self.pause_timer = QTimer()
        #self.pause_timer.timeout.connect(self.continue_time)
        #self.timer.timeout.connect(self.execute_experiment)
        #self.time_count = 0

        #self.send_data_point.connect(self.screen.get_data_point)
        #self.state_changed.connect(
        #    self.ExpEnv._main_window.tabs.tabProgramms.exp_env_buttons[0].state_change
        #)
        #self.state_changed.connect(
        #    self.ExpEnv._main_window.tabs.tabProgramms.exp_env_buttons[1].state_change
        #)
        #self.init_figure_signal.connect(self.screen.init_figure_slot)

    def continue_experiment(self):
        #self.timer.start(500)
        #self.pause_timer.stop()
        self.state = States.RUNNING
        self.change_state(self.state)

    def start_experiment(self):
        # self.init_figure_signal.emit()

        # publish via mqtt
        mqttmsg = StatusMessage(self.name, "Calibration started.", None, None, None)
        if self.mqtt.connection_test():
            self.mqtt.publish_message(mqttmsg)
        #self.timer.start(500)
        self.state = States.RUNNING
        self.change_state(self.state)

    #def execute_experiment(self):
        #old = self.time_count
        #self.time_count += 0.5
        #for time_toggle in self.course_pump_constant:
        #    if old < time_toggle <= self.time_count:
        #        self.ExpEnv.vosekast.pump_constant_tank.toggle()

        #for time_toggle in self.course_pump_measuring:
        #    if old < time_toggle <= self.time_count:
        #        self.ExpEnv.vosekast.pump_measuring_tank.toggle()

        #t = self.time_count
        #store = self.ExpEnv.vosekast.VosekastStore

        #states = store.get_state()
        #for a in states:
        #    self.send_new_data_point(t, states[a]["State"], 0, a + " State")
        #self.send_new_data_point(t, states["Scale"]["Value"], 1, "Scale Value")

    def pause_experiment(self):
        #self.timer.stop()
        #self.pause_timer.start(500)
        self.state = States.PAUSE
        self.change_state(self.state)

    #def continue_time(self):
        #self.time_count += 0.5

    def send_new_data_point(self, x, y, index, legend):
        # self.send_data_point.emit(x, y, index, legend)

        # publish via mqtt
        mqttmsg = StatusMessage(self.name, str(
            x, y, index, legend), "data point", None, None)
        if self.mqtt.connection_test():
            self.mqtt.publish_message(mqttmsg)

    def change_state(self, new_state):
        # self.state_changed.emit(States(new_state).value)

        # publish via mqtt
        mqttmsg = StatusMessage(self.name, States(new_state).value, None, None, None)
        if self.mqtt.connection_test():
            self.mqtt.publish_message(mqttmsg)

    # @pyqtSlot()
    # def stop_experiment_slot(self):
    #     if self.state != States.READY:
    #         self.state = States.STOPPED
    #     self.timer.stop()
    #     self.change_state(self.state)
    #     self.time_count = 0
