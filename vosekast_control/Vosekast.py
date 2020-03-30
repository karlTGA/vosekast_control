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
from vosekast_control.utils.Msg import StatusMessage

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


class Vosekast():

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
            self.level_sensors = [self.level_measuring_high, self.level_measuring_low, self.level_constant_high, self.level_constant_low]

            # pumps
            self.pump_constant_tank = Pump(
                self,
                "pump_constant_tank",
                PIN_PUMP_CONSTANT,
                self._gpio_controller,
            )
            self.pump_measuring_tank = Pump(
                self,
                "pump_measuring_tank",
                PIN_PUMP_MEASURING,
                self._gpio_controller,
            )
            self.pumps = [self.pump_measuring_tank, self.pump_constant_tank]

            # tanks
            self.stock_tank = Tank(
                "stock_tank",
                200,
                None,
                None,
                None,
                None,
                None,
                vosekast=self
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

            self.tanks = [self.stock_tank,
                          self.constant_tank, self.measuring_tank]

            # scale
            self.scale = Scale('measuring_scale', self, emulate=self.emulate)

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
            self.measuring_drain_valve.is_closed
            and not self.measuring_tank.is_filled
        )
        constant_pump_running = self.pump_constant_tank.is_running

        if constant_tank_ready and measuring_tank_ready and constant_pump_running:
            self.logger.info("Ready to start measuring.")

        return constant_tank_ready and measuring_tank_ready and constant_pump_running

    async def empty(self):
        self._state = self.EMPTYING
        self.logger.warning(
            "Emptying Measuring and Constant Tank. Please be aware Stock Tank might overflow.")
        self.pump_measuring_tank.start()
        self.pump_constant_tank.stop()
        self.measuring_tank_switch.close()
        self.measuring_drain_valve.open()

        while self._state == self.EMPTYING:
            await asyncio.sleep(1)

        self.pump_measuring_tank.stop()

    async def shutdown(self):

        self.clean()
        self.logger.info("Shutting down.")

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

        self.logger.debug('Vosekast stopped.')

    def state_overview(self):
        # for tank in self.tanks:
        #     MQTTConnection.publish_message(StatusMessage('tank', tank.name, tank.state))
        # for pump in self.pumps:
        #     MQTTConnection.publish_message(StatusMessage('pump', pump.name, pump.state))
        # for valve in self.valves:
        #     MQTTConnection.publish_message(StatusMessage('valve', valve.name, valve.state))
        # for level_sensor in self.level_sensors:
        #     MQTTConnection.publish_message(StatusMessage('level_sensor', level_sensor.name, level_sensor.state))
        
        for device in self.tanks + self.pumps + self.valves + self.level_sensors:
            device.publish_state()

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
                            f'target_id found. command {command["command"]} did not execute.')

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
                            f'target_id found. command {command["command"]} did not execute.')

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
                    # if command['command'] == '_handle_drained':
                    #     tank._handle_drained()
                    #     return
                    # if command['command'] == '_handle_filling':
                    #     tank._handle_filling()
                    #     return
                    else:
                        self.logger.warning(
                            f'target_id found. command {command["command"]} did not execute.')

                    return

            self.logger.warning(
                f'target_id {command["target_id"]} could not be found.')

        # scales
        elif command['target'] == 'scale':
            if command['target_id'] == 'measuring_scale':
                if command['command'] == 'open_connection':
                    self.scale.open_connection()
                elif command['command'] == 'close_connection':
                    self.scale.close_connection()
                elif command['command'] == 'start_measurement_thread':
                    self.scale.start_measurement_thread()
                elif command['command'] == 'stop_measurement_thread':
                    self.scale.stop_measurement_thread()
                elif command['command'] == 'print_diagnostics':
                    self.scale.print_diagnostics()

                else:
                    self.logger.warning(
                        f'target_id found. command {command["command"]} did not execute.')

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
                elif command['command'] == 'start_sequence':
                    await self.testsequence.start_sequence()
                elif command['command'] == 'stop_sequence':
                    await self.testsequence.stop_sequence()
                elif command['command'] == 'empty_tanks':
                    await self.empty()
                elif command['command'] == 'pause_sequence':
                    self.testsequence.pause_sequence()
                elif command['command'] == 'continue_sequence':
                    await self.testsequence.continue_sequence()
                elif command['command'] == 'state_overview':
                    self.state_overview()

                else:
                    self.logger.warning(
                        f'target_id found. command {command["command"]} did not execute.')

                return

            self.logger.warning(
                f'target_id {command["target_id"]} could not be found.')

        # exception
        else:
            self.logger.warning(
                f'target {command["target"]} could not be found.')


class NoGPIOControllerError(Exception):
    pass
