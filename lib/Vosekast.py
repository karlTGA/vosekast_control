from lib.Pump import Pump
from lib.Tank import Tank
from lib.LevelSensor import LevelSensor
from lib.Valve import Valve
from lib.Scale import Scale
import logging
import asyncio
from lib.Log import LOGGER, add_mqtt_logger_handler
from lib.ExperimentEnvironment import ExperimentEnvironment
from lib.Store import VosekastStore
from lib.MQTT import MQTTController
from lib.MQTT import MQTTCommandHandler



# Vosekast States
INITED = "INITED"
MEASURING = "MEASURING"
PREPARING_MEASURMENT = "PREPARING_MEASUREMENT"
TIME_stop = "time_stop"
WAS_MEASURE = "was_measure"
WEIGHT_start = "weight_start"
WEIGHT_stop = "weight_stop"

# GPIO Assignment
PIN_PUMP_BASE = 17
PIN_PUMP_MEASURING = 27
PIN_VALVE_MEASURING_SWITCH = 12
PIN_VALVE_MEASURING_DRAIN = 18
PIN_LEVEL_MEASURING_HIGH = 24
PIN_LEVEL_MEASURING_LOW = 25
PIN_LEVEL_BASE_LOW = 5

# PUMP IDS
BASE_PUMP = "BASE_PUMP"
MEASURING_PUMP = "MEASURING_PUMP"

# VALVE IDS
MEASURING_TANK_VALVE = "MEASURING_TANK_VALVE"
MEASURING_TANK_SWITCH = "MEASURING_TANK_SWITCH"

# TANK IDS
STOCK_TANK = "STOCK_TANK"
BASE_TANK = "BASE_TANK"
MEASURING_TANK = "MEASURING_TANK"


class Vosekast():
    def __init__(self, gpio_controller, gui_main_window, debug=False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.debug = debug
        self.logger = logging.getLogger(LOGGER)
        self.mqtt_client = MQTTController('localhost')
        self.mqtt_command = MQTTCommandHandler()
        add_mqtt_logger_handler(self.mqtt_client)

        try:
            self._gpio_controller = gpio_controller
            # define how the pins a numbered on the board
            self._gpio_controller.setmode(self._gpio_controller.BCM)

            # main window of the gui
            self._main_window = gui_main_window

            # add store to create checkboxes
            self.VosekastStore = VosekastStore(self)
            self._main_window.tabs.tabProgramms.create_checkboxes(
                self.VosekastStore)

            # valves
            valve_measuring_button = self._main_window.tabs.tabStatus.valve_buttons[
                MEASURING_TANK_VALVE
            ]
            self.measuring_drain_valve = Valve(
                self,
                "Measuring Drain Valve",
                PIN_VALVE_MEASURING_DRAIN,
                Valve.TWO_WAY,
                Valve.BINARY,
                self._gpio_controller,
                valve_measuring_button,
            )
            switch_measuring_button = self._main_window.tabs.tabStatus.valve_buttons[
                MEASURING_TANK_SWITCH
            ]
            self.measuring_tank_switch = Valve(
                self,
                "Measuring Tank Switch",
                PIN_VALVE_MEASURING_SWITCH,
                Valve.SWITCH,
                Valve.BINARY,
                self._gpio_controller,
                switch_measuring_button,
            )
            self.valves = [self.measuring_drain_valve,
                           self.measuring_tank_switch]

            # throttle
            # self.volume_flow_throttle = Valve('VOLUME_FLOW_THROTTLE', PIN, Valve.SWITCH, Valve.BINARY, self._gpio_controller)

            # level_sensors
            self.level_measuring_high = LevelSensor(
                "LEVEL_MEASURING_UP",
                PIN_LEVEL_MEASURING_HIGH,
                bool,
                LevelSensor.HIGH,
                self._gpio_controller,
            )
            self.level_measuring_low = LevelSensor(
                "LEVEL_MEASURING_LOW",
                PIN_LEVEL_MEASURING_LOW,
                bool,
                LevelSensor.LOW,
                self._gpio_controller,
            )
            self.level_base_low = LevelSensor(
                "LEVEL_BASE_LOW",
                PIN_LEVEL_BASE_LOW,
                bool,
                LevelSensor.LOW,
                self._gpio_controller,
            )

            # pumps
            self.pump_base_tank = Pump(
                self,
                "Pump Base Tank",
                PIN_PUMP_BASE,
                self._gpio_controller,
            )
            self.pump_measuring_tank = Pump(
                self,
                "Pump Measuring Tank",
                PIN_PUMP_MEASURING,
                self._gpio_controller,
            )
            self.pumps = [self.pump_measuring_tank, self.pump_base_tank]

            # tanks
            self.stock_tank = Tank(
                STOCK_TANK,
                100,
                None,
                None,
                None,
                None,
                None,
                vosekast=self
            )

            base_tank_gui = self._main_window.tabs.tabStatus.tank_statuses[BASE_TANK]

            self.base_tank = Tank(
                BASE_TANK,
                100,
                None,
                self.level_base_low,
                None,
                None,
                self.pump_base_tank,
                vosekast=self,
                protect_overflow=False,
            )

            measuring_tank_gui = self._main_window.tabs.tabStatus.tank_statuses[
                MEASURING_TANK
            ]

            self.measuring_tank = Tank(
                MEASURING_TANK,
                100,
                None,
                self.level_measuring_low,
                self.level_measuring_high,
                self.measuring_drain_valve,
                self.pump_measuring_tank,
                vosekast=self,
                protect_draining=False,
            )

            self.tanks = [self.stock_tank, self.base_tank, self.measuring_tank]

            # scale
            scale_gui = self._main_window.tabs.tabStatus.scale_status
            self.scale = Scale(self, scale_gui, emulate=self.debug)
            self.scale.open_connection()

            # experiment_environment
            expEnv0 = ExperimentEnvironment(
                20, vosekast=self, main_window=self._main_window
            )

            button_start_pause_exp = self._main_window.tabs.tabProgramms.exp_env_buttons[
                0
            ]
            button_stop_exp = self._main_window.tabs.tabProgramms.exp_env_buttons[1]

            button_start_pause_exp.set_control_instance(
                expEnv0.actual_experiment)
            button_stop_exp.set_control_instance(expEnv0.actual_experiment)

            self._main_window.tabs.tabProgramms.set_experiments(
                expEnv0.experiments)

            self.state = INITED

        except NoGPIOControllerError:
            self.logger.error(
                "You have to add a gpio controller to control or simulate the components."
            )

    def prepare_measuring(self):
        """
        before we can measure we have to prepare the station
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
        measuring_tank_ready = (
            self.measuring_drain_valve == self.measuring_drain_valve.CLOSED
            and self.measuring_tank.state != self.measuring_tank.FILLED
        )
        base_pump_running = self.pump_base_tank.state == self.pump_base_tank.RUNNING

        # return base_tank_ready and measuring_tank_ready and base_pump_running
        return True

    async def shutdown(self):
        # drain the measuring tank
        self.measuring_tank.drain_tank()
        self.logger.info("Measuring tank is emptied.")
        self.clean()
        self.logger.info("Vosekast is shut down.")
        await self.mqtt_client.disconnect()

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

    async def run(self):
        self.logger.debug("I started")
        await self.mqtt_client.connect()


class NoGPIOControllerError(Exception):
    pass
