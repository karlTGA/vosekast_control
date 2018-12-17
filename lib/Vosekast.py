from lib.Pump import Pump
from lib.Tank import Tank
from lib.LevelSensor import LevelSensor
from lib.Valve import Valve
from lib.Scale import Scale
import logging
from lib.Log import LOGGER
from lib.ExperimentEnvironment import ExperimentEnvironment
from lib.ExperimentEnvironmentNew import ExperimentEnvironmentNew
from PyQt5.QtCore import QThread


# Vorsekast States
INITED = 'INITED'
MEASURING = 'MEASURING'
PREPARING_MEASURMENT = 'PREPARING_MEASURMENT'
TIME_stop = 'time_stop'
WAS_MEASURE = 'was_measure'
WEIGHT_start = 'weight_start'
WEIGHT_stop = 'weight_stop'

# GPIO Assignment
PIN_PUMP_BASE = 17
PIN_PUMP_MEASURING = 27
PIN_VALVE_MEASURING_SWITCH = 12
PIN_VALVE_MEASURING_DRAIN = 18
PIN_LEVEL_MEASURING_HIGH = 24
PIN_LEVEL_MEASURING_LOW = 25
PIN_LEVEL_BASE_LOW = 5

# PUMP IDS
BASE_PUMP = 'BASE_PUMP'
MEASURING_PUMP = 'MEASURING_PUMP'

# VALVE IDS
MEASURING_TANK_VALVE = 'MEASURING_TANK_VALVE'
MEASURING_TANK_SWITCH = 'MEASURING_TANK_SWITCH'

# TANK IDS
STOCK_TANK = 'STOCK_TANK'
BASE_TANK = 'BASE_TANK'
MEASURING_TANK = 'MEASURING_TANK'

class Vosekast(QThread):

    def __init__(self, gpio_controller, gui_main_window, debug=False):
        self.debug = debug
        self.logger = logging.getLogger(LOGGER)
        self.app = QCoreApplication.instance()

        try:
            self._gpio_controller = gpio_controller
            # define how the pins a numbered on the board
            self._gpio_controller.setmode(self._gpio_controller.BCM)

            # main window of the gui
            self._main_window = gui_main_window

            # valves
            valve_measuring_button = self._main_window.tabs.tabStatus.valve_buttons[MEASURING_TANK_VALVE]
            self.measuring_drain_valve = Valve(MEASURING_TANK_VALVE, PIN_VALVE_MEASURING_DRAIN, Valve.TWO_WAY, Valve.BINARY, self._gpio_controller, valve_measuring_button)
            switch_measuring_button = self._main_window.tabs.tabStatus.valve_buttons[MEASURING_TANK_SWITCH]
            self.measuring_tank_switch = Valve(MEASURING_TANK_SWITCH, PIN_VALVE_MEASURING_SWITCH, Valve.SWITCH, Valve.BINARY, self._gpio_controller, switch_measuring_button)
            self.valves = [self.measuring_drain_valve, self.measuring_tank_switch]

            # throttle
            # self.volume_flow_throttle = Valve('VOLUME_FLOW_THROTTLE', PIN, Valve.SWITCH, Valve.BINARY, self._gpio_controller)

            # level_sensors
            self.level_measuring_high = LevelSensor('LEVEL_MEASURING_UP', PIN_LEVEL_MEASURING_HIGH, bool, LevelSensor.HIGH, self._gpio_controller)
            self.level_measuring_low = LevelSensor('LEVEL_MEASURING_LOW', PIN_LEVEL_MEASURING_LOW, bool, LevelSensor.LOW, self._gpio_controller)
            self.level_base_low = LevelSensor('LEVEL_BASE_LOW', PIN_LEVEL_BASE_LOW, bool, LevelSensor.LOW, self._gpio_controller)

            # pumps
            pump_base_button = self._main_window.tabs.tabStatus.pump_buttons[BASE_PUMP]
            self.pump_base_tank = Pump(BASE_PUMP, PIN_PUMP_BASE, self._gpio_controller, pump_base_button)
            pump_measuring_button = self._main_window.tabs.tabStatus.pump_buttons[MEASURING_PUMP]
            self.pump_measuring_tank = Pump(MEASURING_PUMP, PIN_PUMP_MEASURING, self._gpio_controller, pump_measuring_button)
            self.pumps = [self.pump_measuring_tank, self.pump_base_tank]

            # tanks
            self.stock_tank = Tank(STOCK_TANK, 100, None, None, None, None, None, None)
            base_tank_gui = self._main_window.tabs.tabStatus.tank_statuses[BASE_TANK]
            self.base_tank = Tank(BASE_TANK, 100, None, self.level_base_low, None, None, self.pump_base_tank, base_tank_gui, protect_overflow=False)
            measuring_tank_gui = self._main_window.tabs.tabStatus.tank_statuses[MEASURING_TANK]
            self.measuring_tank = Tank(MEASURING_TANK, 100, None, self.level_measuring_low, self.level_measuring_high, self.measuring_drain_valve, self.pump_measuring_tank, measuring_tank_gui, protect_draining=False)
            self.tanks = [self.stock_tank, self.base_tank, self.measuring_tank]

            # scale
            scale_gui = self._main_window.tabs.tabStatus.scale_status
            self.scale = Scale(scale_gui, emulate=self.debug)
            self.scale.open_connection()

            # experiment_environment
            button_exp_env_0 = self._main_window.tabs.tabProgramms.exp_env_buttons[0]
            button_exp_env_1 = self._main_window.tabs.tabProgramms.exp_env_buttons[1]
            button_exp_env_2 = self._main_window.tabs.tabProgramms.exp_env_buttons[2]
            expEnv = ExperimentEnvironment(20, vosekast=self, main_window=self._main_window, index=0, funcs=['sin', 'cos', 'sqrt', 'log'])
            expEnv2 = ExperimentEnvironment(20, vosekast=self, main_window=self._main_window, index=1, funcs=['sin', 'cos', 'sqrt', 'pump_base'])
            expEnv3 = ExperimentEnvironmentNew(20, vosekast=self, main_window=self._main_window, index=2, funcs=['sin', 'cos', 'sqrt', 'pump_base'])

            self.state = INITED

        except NoGPIOControllerError:
            self.logger.error('You have to add a gpio controller to control or simulate the components.')

    def prepare_measuring(self):
        """
        before we can measur we have to prepare the station
        :return:
        """
        # fill the base tank
        self.base_tank.prepare_to_fill()
        self.pump_base_tank.start()
        self.state = PREPARING_MEASURMENT

    def ready_to_measure(self):
        """
        is vosekast ready to measure
        :return: measuring ready
        """
        base_tank_ready = self.base_tank.state == self.base_tank.FILLED
        measuring_tank_ready = self.measuring_drain_valve == self.measuring_drain_valve.CLOSED and self.measuring_tank.state != self.measuring_tank.FILLED
        base_pump_running = self.pump_base_tank.state == self.pump_base_tank.RUNNING

        # return base_tank_ready and measuring_tank_ready and base_pump_running
        return True

    def shutdown(self):
        # drain the measuring tank
        self.measuring_tank.drain_tank()
        self.logger.info("Measuring tank is emptied.")
        self.clean()
        self.logger.info("Vosekast is shutdown.")

    def clean(self):
        # shutdown pumps
        for pump in self.pumps:
            pump.stop()

        # close valves
        for valve in self.valves:
            valve.close()

        # stop scale
        self.scale.stop_measurement_thread()
        self.scale.close_connection()

    def run():
        self.logger.debug('I started')

class NoGPIOControllerError(Exception):
    pass
