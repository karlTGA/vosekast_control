from lib.Pump import Pump
from lib.Tank import Tank
from lib.LevelSensor import LevelSensor
from lib.Valve import Valve
from lib.Scale import Scale
import logging
import asyncio
from lib.Log import LOGGER, add_mqtt_logger_handler
#from lib.ExperimentEnvironment import ExperimentEnvironment
from lib.Store import VosekastStore
from lib.MQTT import MQTTController


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
    def __init__(self, gpio_controller, debug=False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.debug = debug
        self.logger = logging.getLogger(LOGGER)
        self.mqtt_client = MQTTController('localhost')
        self.mqtt_client.on_command = self.handle_command
        add_mqtt_logger_handler(self.mqtt_client)
        # new

        try:
            self._gpio_controller = gpio_controller
            # define how the pins are numbered on the board
            self._gpio_controller.setmode(self._gpio_controller.BCM)

            # add store to create checkboxes
            self.VosekastStore = VosekastStore(self)

            # valves
            self.measuring_drain_valve = Valve(
                self,
                "Measuring Drain Valve",
                PIN_VALVE_MEASURING_DRAIN,
                Valve.TWO_WAY,
                Valve.BINARY,
                self._gpio_controller,
            )
            self.measuring_tank_switch = Valve(
                self,
                "Measuring Tank Switch",
                PIN_VALVE_MEASURING_SWITCH,
                Valve.SWITCH,
                Valve.BINARY,
                self._gpio_controller,
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
                "Stock Tank",
                100,
                None,
                None,
                None,
                None,
                None,
                vosekast=self
            )

            self.base_tank = Tank(
                "Base Tank",
                100,
                None,
                self.level_base_low,
                None,
                None,
                self.pump_base_tank,
                vosekast=self,
                protect_overflow=False,
            )

            self.measuring_tank = Tank(
                "Measuring Tank",
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
            self.scale = Scale(self, emulate=self.debug)
            self.scale.open_connection()

            # experiment_environment
            # expEnv0 = ExperimentEnvironment(
            #     20, vosekast=self, main_window=self._main_window
            # )

            # button_start_pause_exp = self._main_window.tabs.tabProgramms.exp_env_buttons[
            #     0
            # ]
            # button_stop_exp = self._main_window.tabs.tabProgramms.exp_env_buttons[1]

            # button_start_pause_exp.set_control_instance(
            #     expEnv0.actual_experiment)
            # button_stop_exp.set_control_instance(expEnv0.actual_experiment)

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
        self.logger.info("Measuring tank is empty.")
        self.clean()
        self.logger.info("Vosekast is shutting down.")
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
        self.logger.debug("Vosekast started ok.")
        await self.mqtt_client.connect()

    # handle incoming mqtt commands
    async def handle_command(self, command):
        # valves
        if command['target'] == 'valve':
            for valve in self.valves:
                target_id = command['target_id']
                if valve.name == target_id:
                    if command['command'] == 'close':
                        valve.close()
                    if command['command'] == 'open':
                        valve.open()
                    else:
                        self.logger.warning(
                            f'command {command["command"]} did not execute.')

                    return

            self.logger.warning(
                f'target_id {command["target_id"]} could not be found.')

        # pumps
        elif command['target'] == 'pump':
            for pump in self.pumps:
                target_id = command['target_id']
                if pump.name == target_id:
                    if command['command'] == 'start':
                        pump.start()
                    if command['command'] == 'stop':
                        pump.stop()
                    if command['command'] == 'toggle':
                        pump.toggle()
                    else:
                        self.logger.warning(
                            f'command {command["command"]} did not execute.')

                    return

            self.logger.warning(
                f'target_id {command["target_id"]} could not be found.')

        # tanks
        elif command['target'] == 'tank':
            for tank in self.tanks:
                target_id = command['target_id']
                if tank.name == target_id:
                    if command['command'] == 'drain_tank':
                        tank.drain_tank()
                        return
                    if command['command'] == 'prepare_to_fill':
                        tank.prepare_to_fill()
                    else:
                        self.logger.warning(
                            f'command {command["command"]} did not execute.')

                    return

            self.logger.warning(
                f'target_id {command["target_id"]} could not be found.')

        # scales
        elif command['target'] == 'scale':
            if command['target_id'] == 'scale':
                if command['command'] == 'open_connection':
                    self.scale.open_connection()
                elif command['command'] == 'close_connection':
                    self.scale.close_connection()
                elif command['command'] == 'start_measurement_thread':
                    self.scale.start_measurement_thread()
                elif command['command'] == 'stop_measurement_thread':
                    self.scale.stop_measurement_thread()
                elif command['command'] == 'get_stable_value':
                    self.scale.get_stable_value()
                elif command['command'] == 'loop':
                    self.scale.loop()
                elif command['command'] == 'read_value_from_scale':
                    self.scale.read_value_from_scale()
                else:
                    self.logger.warning(
                        f'command {command["command"]} did not execute.')

                return

            self.logger.warning(
                f'target_id {command["target_id"]} could not be found.')

        # system
        elif command['target'] == 'system':
            if command['target_id'] == 'system':
                if command['command'] == 'shutdown':
                    await self.shutdown()
                elif command['command'] == 'clean':
                    self.clean()
                elif command['command'] == 'prepare_measuring':
                    self.prepare_measuring()
                elif command['command'] == 'ready_to_measure':
                    self.ready_to_measure()
                else:
                    self.logger.warning(
                        f'command {command["command"]} did not execute.')

                return

            self.logger.warning(
                f'target_id {command["target_id"]} could not be found.')

        # exception
        else:
            self.logger.warning(
                f'target {command["target"]} could not be found.')


class NoGPIOControllerError(Exception):
    pass
