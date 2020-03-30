from vosekast_control.Pump import Pump
from vosekast_control.Tank import Tank
from vosekast_control.LevelSensor import LevelSensor
from vosekast_control.Valve import Valve
from vosekast_control.Scale import Scale
from vosekast_control.TestSequence import TestSequence

import logging
import asyncio
import csv
import sqlite3
from sqlite3 import Error
from vosekast_control.Log import LOGGER, add_mqtt_logger_handler

from vosekast_control.connectors import MQTTConnection

import os


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


class Vosekast:

    # Vosekast States
    INITED = "INITED"
    RUNNING = "RUNNING"
    MEASURING = "MEASURING"
    PREPARING_MEASUREMENT = "PREPARING_MEASUREMENT"
    EMPTYING = "EMPTYING"

    def __init__(self, app_control, gpio_controller, emulate=False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.emulate = emulate
        self.logger = logging.getLogger(LOGGER)
        self._app_control = app_control

        # set mqtt client, host
        MQTTConnection.on_command = self.handle_command
        add_mqtt_logger_handler(MQTTConnection)

        try:
            self._gpio_controller = gpio_controller
            # define how the pins are numbered on the board
            self._gpio_controller.setmode(self._gpio_controller.BCM)

            # valves
            self.measuring_drain_valve = Valve(
                self,
                "measuring_drain_valve",
                PIN_VALVE_MEASURING_DRAIN,
                Valve.TWO_WAY,
                Valve.BINARY,
                self._gpio_controller,
            )
            self.measuring_tank_switch = Valve(
                self,
                "measuring_tank_switch",
                PIN_VALVE_MEASURING_SWITCH,
                Valve.SWITCH,
                Valve.BINARY,
                self._gpio_controller,
            )
            self.valves = [self.measuring_drain_valve, self.measuring_tank_switch]

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
                self, "pump_constant_tank", PIN_PUMP_CONSTANT, self._gpio_controller,
            )
            self.pump_measuring_tank = Pump(
                self, "pump_measuring_tank", PIN_PUMP_MEASURING, self._gpio_controller,
            )
            self.pumps = [self.pump_measuring_tank, self.pump_constant_tank]

            # tanks
            self.stock_tank = Tank(
                "stock_tank", 200, None, None, None, None, None, vosekast=self
            )

            self.constant_tank = Tank(
                "constant_tank",
                100,
                None,
                self.level_constant_low,
                self.level_constant_high,
                None,
                self.pump_constant_tank,
                vosekast=self,
                protect_overflow=False,
                emulate=self.emulate,
            )

            self.measuring_tank = Tank(
                "measuring_tank",
                100,
                None,
                self.level_measuring_low,
                self.level_measuring_high,
                self.measuring_drain_valve,
                self.pump_measuring_tank,
                vosekast=self,
                protect_draining=False,
                emulate=self.emulate,
            )

            self.tanks = [self.stock_tank, self.constant_tank, self.measuring_tank]

            # scale
            self.scale = Scale("measuring_scale", self, emulate=self.emulate)

            # testsequence
            self.testsequence = TestSequence(self, emulate=self.emulate)

            # change state if ok
            self._state = self.INITED

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
        self.pump_measuring_tank.stop()
        self._state = self.PREPARING_MEASUREMENT

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        self._state = new_state
        self.logger.debug(f"New Vosekast state is: {new_state}")

    @property
    def ready_to_measure(self):
        """
        is vosekast ready to measure
        :return: measuring ready
        """

        constant_tank_ready = self.constant_tank.is_filled

        measuring_tank_ready = (
            self.measuring_drain_valve.is_closed and not self.measuring_tank.is_filled
        )
        constant_pump_running = self.pump_constant_tank.is_running

        if constant_tank_ready and measuring_tank_ready and constant_pump_running:
            self.logger.info("Ready to start measuring.")

        return constant_tank_ready and measuring_tank_ready and constant_pump_running

    async def empty(self):
        self._state = self.EMPTYING
        self.logger.warning(
            "Emptying Measuring and Constant Tank. Please be aware Stock Tank might overflow."
        )
        self.pump_measuring_tank.start()
        self.pump_constant_tank.stop()
        self.measuring_tank_switch.close()
        self.measuring_drain_valve.open()

        while self._state == self.EMPTYING:
            await asyncio.sleep(1)

        self.pump_measuring_tank.stop()

    # def create_file(self):
    # # create file, write header to csv file
    # with open('sequence_values.csv', 'w', newline='') as file:
    #     writer = csv.writer(file, delimiter=',',
    #                         quotechar='|', quoting=csv.QUOTE_MINIMAL)
    #     writer.writerow(["timestamp", "scale value", "flow",
    #                      "average flow from last 5 values"])

    async def shutdown(self):

        self.clean()
        self.logger.info("Shutting down.")

        # # GPIO cleanup
        # self._gpio_controller.cleanup()
        # self.logger.debug("GPIO cleanup.")

        await MQTTConnection.disconnect()
        self.logger.debug("MQTT client disconnected.")

        self._app_control.shutdown()

    def clean(self):
        self.testsequence.state = self.testsequence.STOPPED
        self.measuring_tank.drain_tank()
        self.logger.debug("Draining measuring tank.")

        # set fill countdown to False
        for tank in self.tanks:
            tank.state = "STOPPED"

        # shutdown pumps
        for pump in self.pumps:
            pump.stop()

        self.logger.debug("All pumps switched off.")

        # stop scale
        self.logger.debug("Now stopping measurement thread.")
        self.scale.stop_measurement_thread()
        self.scale.close_connection()

    async def run(self):
        if self.emulate:
            self.logger.info("Start Vosekast in Debug Mode.")

        self.scale.start()

        await MQTTConnection.connect()
        self._state = self.RUNNING
        self.logger.debug("Vosekast started ok.")

        if self.emulate:
            self.logger.info("Starting sequence in 7s.")
            await asyncio.sleep(7)
            await self.testsequence.start_sequence()

        while not self._app_control.is_terminating():
            await asyncio.sleep(1)

        self.logger.debug("Vosekast stopped.")

    # handle incoming mqtt commands
    async def handle_command(self, command):
        target = command.get("target")
        target_id = command.get("target_id")
        command_id = command.get("command")

        if target == "valve":
            for valve in self.valves:
                if valve.name == target_id:
                    if command_id == "close":
                        valve.close()
                        return
                    elif command_id == "open":
                        valve.open()
                        return
                    else:
                        self.logger.warning(
                            f"receive unknown command {command_id} for \
                            target_id {target_id}."
                        )

                    return

            self.logger.warning(
                f"target_id {target_id} could not \
                is unknown."
            )

        # pumps
        elif target == "pump":
            for pump in self.pumps:
                target_id = target_id
                if pump.name == target_id:
                    if command_id == "start":
                        pump.start()
                    elif command_id == "stop":
                        pump.stop()
                    elif command_id == "toggle":
                        pump.toggle()
                    else:
                        self.logger.warning(
                            f"receive unknown command {command_id} for \
                            target_id {target_id}."
                        )

                    return

            self.logger.warning(f"target_id {target_id} is unknown.")

        # tanks
        elif target == "tank":
            for tank in self.tanks:
                target_id = target_id
                if tank.name == target_id:
                    if command_id == "drain_tank":
                        tank.drain_tank()
                    elif command_id == "prepare_to_fill":
                        tank.prepare_to_fill()
                    else:
                        self.logger.warning(
                            f"receive unknown command {command_id} for \
                            target_id {target_id}."
                        )

                    return

            self.logger.warning(f"target_id {target_id} could not be found.")

        # scales
        elif target == "scale":
            if target_id == "measuring_scale":
                if command_id == "open_connection":
                    self.scale.open_connection()
                elif command_id == "close_connection":
                    self.scale.close_connection()
                elif command_id == "start_measurement_thread":
                    self.scale.start_measurement_thread()
                elif command_id == "stop_measurement_thread":
                    self.scale.stop_measurement_thread()
                elif command_id == "print_diagnostics":
                    self.scale.print_diagnostics()

                else:
                    self.logger.warning(
                        f"receive unknown command {command_id} for \
                            target_id {target_id}."
                    )

                return

            self.logger.warning(f"target_id {target_id} could not be found.")

        # system
        elif target == "system":
            if target_id == "system":
                if command_id == "shutdown":
                    await self.shutdown()
                elif command_id == "clean":
                    self.clean()
                elif command_id == "prepare_measuring":
                    self.prepare_measuring()
                elif command_id == "start_sequence":
                    await self.testsequence.start_sequence()
                elif command_id == "stop_sequence":
                    await self.testsequence.stop_sequence()
                elif command_id == "empty_tanks":
                    await self.empty()
                elif command_id == "pause_sequence":
                    self.testsequence.pause_sequence()
                elif command_id == "continue_sequence":
                    await self.testsequence.continue_sequence()

                else:
                    self.logger.warning(
                        f"receive unknown command {command_id} for \
                            target_id {target_id}."
                    )

                return

            self.logger.warning(f"target_id {target_id} is unknown.")

        # exception
        else:
            self.logger.warning(f"command target {target} is unknown.")


class NoGPIOControllerError(Exception):
    pass
