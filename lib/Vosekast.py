from lib.Pump import Pump
from lib.Tank import Tank
from lib.LevelSensor import LevelSensor
from lib.Valve import Valve
from lib.Scale import Scale
from lib.TestSequence import TestSequence
import logging
import asyncio
import csv
from lib.Log import LOGGER, add_mqtt_logger_handler
#from lib.ExperimentEnvironment import ExperimentEnvironment
#from lib.Store import VosekastStore
from lib.MQTT import MQTTController

import os

# Vosekast States
INITED = "INITED"
MEASURING = "MEASURING"
PREPARING_MEASURMENT = "PREPARING_MEASUREMENT"
TIME_stop = "time_stop"
WAS_MEASURE = "was_measure"
WEIGHT_start = "weight_start"
WEIGHT_stop = "weight_stop"

# GPIO Assignment
PIN_PUMP_CONSTANT = 17
PIN_PUMP_MEASURING = 27
PIN_VALVE_MEASURING_SWITCH = 22
PIN_VALVE_MEASURING_DRAIN = 18
PIN_LEVEL_MEASURING_HIGH = 24
PIN_LEVEL_MEASURING_LOW = 25
PIN_LEVEL_CONSTANT_LOW = 5
PIN_LEVEL_CONSTANT_HIGH = 6

# PUMP IDS
CONSTANT_PUMP = "CONSTANT_PUMP"
MEASURING_PUMP = "MEASURING_PUMP"

# VALVE IDS
MEASURING_TANK_VALVE = "MEASURING_TANK_VALVE"
MEASURING_TANK_SWITCH = "MEASURING_TANK_SWITCH"

# TANK IDS
STOCK_TANK = "STOCK_TANK"
CONSTANT_TANK = "CONSTANT_TANK"
MEASURING_TANK = "MEASURING_TANK"


class Vosekast():
    def __init__(self, gpio_controller, debug=False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.debug = debug
        self.logger = logging.getLogger(LOGGER)

        # set mqtt client, host
        self.mqtt_client = MQTTController('localhost')
        self.mqtt_client.on_command = self.handle_command
        add_mqtt_logger_handler(self.mqtt_client)

        try:
            self._gpio_controller = gpio_controller
            # define how the pins are numbered on the board
            self._gpio_controller.setmode(self._gpio_controller.BCM)

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
            self.level_constant_low = LevelSensor(
                "LEVEL_CONSTANT_LOW",
                PIN_LEVEL_CONSTANT_LOW,
                bool,
                LevelSensor.LOW,
                self._gpio_controller,
            )
            self.level_constant_high = LevelSensor(
                "LEVEL_CONSTANT_HIGH",
                PIN_LEVEL_CONSTANT_HIGH,
                bool,
                LevelSensor.HIGH,
                self._gpio_controller,
            )

            # pumps
            self.pump_constant_tank = Pump(
                self,
                "Pump Constant Tank",
                PIN_PUMP_CONSTANT,
                self._gpio_controller,
            )
            self.pump_measuring_tank = Pump(
                self,
                "Pump Measuring Tank",
                PIN_PUMP_MEASURING,
                self._gpio_controller,
            )
            self.pumps = [self.pump_measuring_tank, self.pump_constant_tank]

            # tanks
            self.stock_tank = Tank(
                "Stock Tank",
                200,
                None,
                None,
                None,
                None,
                None,
                vosekast=self
            )

            self.constant_tank = Tank(
                "Constant Tank",
                100,
                None,
                self.level_constant_low,
                self.level_constant_high,
                None,
                self.pump_constant_tank,
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

            self.tanks = [self.stock_tank, self.constant_tank, self.measuring_tank]

            # scale
            self.scale = Scale(self, emulate=self.debug)
            

            # testsequence
            self.testsequence = TestSequence(self)

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
        # close MDV,
        # fill the constant tank
        self.measuring_drain_valve.close()
        self.constant_tank.prepare_to_fill()
        self.pump_constant_tank.start()
        self.state = PREPARING_MEASURMENT

    async def test(self):
        try:
            self.measuring_tank.prepare_to_fill()
            self.pump_measuring_tank.start()
            self.state = PREPARING_MEASURMENT
            self.measuring_tank_switch.open()
            await asyncio.sleep(100)
            self.measuring_drain_valve.close()
            self.pump_measuring_tank.stop()
            self.logger.debug("Test completed.")
        except:
            self.logger.debug("Test aborted.")
      
    def ready_to_measure(self):
        """
        is vosekast ready to measure
        :return: measuring ready
        """

        #constant tank ready
        constant_tank_ready = self.constant_tank.is_filled
        #todo fix
        measuring_tank_ready = (
            self.measuring_drain_valve.is_closed
            and not self.measuring_tank.is_filled
        )
        constant_pump_running = self.pump_constant_tank.is_running

        if constant_tank_ready and measuring_tank_ready and constant_pump_running:
            self.logger.info("Ready to start measuring.")

        return constant_tank_ready and measuring_tank_ready and constant_pump_running
        # return True

    def create_file(self):
        # create file, write header to csv file
        with open('sequence_values.csv', 'w', newline='') as file:
            writer = csv.writer(file, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["timestamp", "scale value"])
        
    async def shutdown(self):
        # drain the measuring tank
        self.measuring_tank.drain_tank()
        self.logger.info("Measuring tank is empty.")
        self.clean()
        self.logger.info("Shutting down.")
        await self.mqtt_client.disconnect()
        os.system('sudo shutdown -h now')

    def clean(self):
        # shutdown pumps
        for pump in self.pumps:
            pump.stop()
        self.logger.debug("All pumps switched off.")

        # close valves
        #for valve in self.valves:
        #    valve.close()
        self.measuring_tank.drain_tank()
        self.logger.debug("Draining measuring tank.")

        self.measuring_tank_switch.close()
        self.logger.debug("Open measuring tank switch.")

        # stop scale
        #self.scale.stop_measurement_thread()
        #self.scale.close_connection()

        try:
            # GPIO cleanup
            self._gpio_controller.cleanup()
            self.logger.debug("GPIO cleanup.")
        except:
            self.logger.warning("GPIO mode not set. Run start_measurement_thread to set GPIO mode.")

    def initialise_gpio(self):
        try:
            self._gpio_controller = gpio_controller
            # define how the pins are numbered on the board
            self._gpio_controller.setmode(self._gpio_controller.BCM)
        except:
            self.logger.error("GPIO setmode failed.")

    async def run(self):
        self.scale.open_connection()
        self.scale.start_measurement_thread()
                
        await self.mqtt_client.connect()
        self.logger.debug("Vosekast started ok.")
                
    # handle incoming mqtt commands
    async def handle_command(self, command):
        # valves
        if command['target'] == 'valve':
            for valve in self.valves:
                target_id = command['target_id']
                if valve.name == target_id:
                    if command['command'] == 'close':
                        valve.close()
                        return
                    if command['command'] == 'open':
                        valve.open()
                        return
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
                        return
                    if command['command'] == '_handle_drained':
                        tank._handle_drained()
                        return
                    if command['command'] == '_handle_filling':
                        tank._handle_filling()
                        return
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
                elif command['command'] == 'print_diagnostics':
                    self.scale.print_diagnostics()
                elif command['command'] == 'read_value_from_scale':
                    self.scale.read_value_from_scale()
                # elif command['command'] == 'toggle_publishing':
                #     self.scale.toggle_publishing()

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
                elif command['command'] == 'start_sequence':
                    await self.testsequence.start_sequence()
                elif command['command'] == 'stop_sequence':
                    self.testsequence.stop_sequence()
                elif command['command'] == 'test':
                    await self.test()
                elif command['command'] == 'clean':
                    self.clean()

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
