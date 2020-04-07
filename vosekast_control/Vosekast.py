from vosekast_control.Pump import Pump
from vosekast_control.Tank import Tank
from vosekast_control.LevelSensor import LevelSensor
from vosekast_control.Valve import Valve
from vosekast_control.Scale import Scale
from vosekast_control.TestrunController import TestrunController

from typing import Dict
import logging
import asyncio
from vosekast_control.Log import LOGGER, add_mqtt_logger_handler

from vosekast_control.connectors import MQTTConnection
from vosekast_control.utils.Msg import InfoMessage, DataMessage
from vosekast_control.utils.Constants import (
    SCALE_MEASURING,
    MEASURING_DRAIN_VALVE,
    PIN_VALVE_MEASURING_SWITCH,
    PIN_VALVE_MEASURING_DRAIN,
    MEASURING_TANK_SWITCH,
    LEVEL_MEASURING_TOP,
    LEVEL_MEASURING_BOTTOM,
    LEVEL_CONSTANT_TOP,
    LEVEL_CONSTANT_BOTTOM,
    PIN_LEVEL_MEASURING_HIGH,
    PIN_LEVEL_MEASURING_LOW,
    PIN_LEVEL_CONSTANT_HIGH,
    PIN_LEVEL_CONSTANT_LOW,
    PUMP_CONSTANT_TANK,
    PUMP_MEASURING_TANK,
    PIN_PUMP_CONSTANT,
    PIN_PUMP_MEASURING,
    CONSTANT_TANK,
    STOCK_TANK,
    MEASURING_TANK,
)


class Vosekast:
    # Vosekast States
    INITED = "INITED"
    RUNNING = "RUNNING"
    MEASURING = "MEASURING"
    PREPARING_MEASUREMENT = "PREPARING_MEASUREMENT"
    EMPTYING = "EMPTYING"

    valves: Dict[str, Valve]
    tanks: Dict[str, Tank]
    pumps: Dict[str, Pump]
    level_sensors: Dict[str, LevelSensor]
    scale: Scale

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

            # init devices
            self._init_valves()
            self._init_level_sensors()
            self._init_pumps()
            self._init_tanks()
            self.scale = Scale(
                name=SCALE_MEASURING, vosekast=self, emulate=self.emulate
            )

            self.testrun_controller = TestrunController(vosekast=self)

            # change state if ok
            self._state = self.INITED

        except NoGPIOControllerError:
            self.logger.error(
                "You have to add a gpio controller to control or simulate the components."
            )

    def _init_valves(self):
        measuring_drain_valve = Valve(
            self,
            MEASURING_DRAIN_VALVE,
            PIN_VALVE_MEASURING_DRAIN,
            Valve.TWO_WAY,
            Valve.BINARY,
            self._gpio_controller,
        )
        measuring_tank_switch = Valve(
            self,
            MEASURING_TANK_SWITCH,
            PIN_VALVE_MEASURING_SWITCH,
            Valve.SWITCH,
            Valve.BINARY,
            self._gpio_controller,
        )
        self.valves = {
            MEASURING_DRAIN_VALVE: measuring_drain_valve,
            MEASURING_TANK_SWITCH: measuring_tank_switch,
        }

    def _init_level_sensors(self):
        level_measuring_top = LevelSensor(
            LEVEL_MEASURING_TOP,
            PIN_LEVEL_MEASURING_HIGH,
            bool,
            LevelSensor.HIGH,
            self._gpio_controller,
        )
        level_measuring_bottom = LevelSensor(
            LEVEL_MEASURING_BOTTOM,
            PIN_LEVEL_MEASURING_LOW,
            bool,
            LevelSensor.LOW,
            self._gpio_controller,
        )
        level_constant_top = LevelSensor(
            LEVEL_CONSTANT_TOP,
            PIN_LEVEL_CONSTANT_HIGH,
            bool,
            LevelSensor.HIGH,
            self._gpio_controller,
        )
        level_constant_bottom = LevelSensor(
            LEVEL_CONSTANT_BOTTOM,
            PIN_LEVEL_CONSTANT_LOW,
            bool,
            LevelSensor.LOW,
            self._gpio_controller,
        )

        self.level_sensors = {
            LEVEL_MEASURING_TOP: level_measuring_top,
            LEVEL_MEASURING_BOTTOM: level_measuring_bottom,
            LEVEL_CONSTANT_TOP: level_constant_top,
            LEVEL_CONSTANT_BOTTOM: level_constant_bottom,
        }

    def _init_pumps(self):
        pump_constant_tank = Pump(
            self, PUMP_CONSTANT_TANK, PIN_PUMP_CONSTANT, self._gpio_controller,
        )
        pump_measuring_tank = Pump(
            self, PUMP_MEASURING_TANK, PIN_PUMP_MEASURING, self._gpio_controller,
        )
        self.pumps = {
            PUMP_CONSTANT_TANK: pump_constant_tank,
            PUMP_MEASURING_TANK: pump_measuring_tank,
        }

    def _init_tanks(self):
        stock_tank = Tank(STOCK_TANK, 200, None, None, None, None, None, vosekast=self)

        constant_tank = Tank(
            CONSTANT_TANK,
            100,
            None,
            self.level_sensors[LEVEL_CONSTANT_BOTTOM],
            self.level_sensors[LEVEL_CONSTANT_TOP],
            None,
            self.pumps[PUMP_CONSTANT_TANK],
            vosekast=self,
            protect_overflow=False,
            emulate=self.emulate,
        )

        measuring_tank = Tank(
            MEASURING_TANK,
            100,
            None,
            self.level_sensors[LEVEL_MEASURING_BOTTOM],
            self.level_sensors[LEVEL_MEASURING_TOP],
            self.valves[MEASURING_DRAIN_VALVE],
            self.pumps[PUMP_MEASURING_TANK],
            vosekast=self,
            protect_draining=False,
            emulate=self.emulate,
        )

        self.tanks = {
            STOCK_TANK: stock_tank,
            CONSTANT_TANK: constant_tank,
            MEASURING_TANK: measuring_tank,
        }

    def prepare_measuring(self):
        """
        before we can measure we have to prepare the station
        :return:
        """
        # close MDV,
        # fill the constant tank
        self.valves[MEASURING_DRAIN_VALVE].close()
        self.tanks[CONSTANT_TANK].prepare_to_fill()
        self.pumps[PUMP_CONSTANT_TANK].start()
        self.pumps[PUMP_MEASURING_TANK].stop()
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

        constant_tank_ready = self.tanks[CONSTANT_TANK].is_filled
        measuring_tank_ready = (
            self.valves[MEASURING_DRAIN_VALVE].is_closed
            and not self.tanks[MEASURING_TANK].is_filled
        )
        constant_pump_running = self.pumps[PUMP_CONSTANT_TANK].is_running

        return constant_tank_ready and measuring_tank_ready and constant_pump_running

    async def empty_tanks(self):
        self._state = self.EMPTYING
        self.logger.warning(
            "Emptying Measuring and Constant Tank. Please be aware Stock Tank might overflow."
        )
        self.pumps[PUMP_MEASURING_TANK].start()
        self.pumps[PUMP_CONSTANT_TANK].stop()
        self.valves[MEASURING_TANK_SWITCH].close()
        self.valves[MEASURING_DRAIN_VALVE].open()

        while self._state == self.EMPTYING:
            await asyncio.sleep(1)

        self.pumps[PUMP_MEASURING_TANK].stop()

    async def shutdown(self):

        await self.clean()
        self.logger.info("Shutting down.")

        await MQTTConnection.disconnect()
        self.logger.debug("MQTT client disconnected.")

        self._app_control.shutdown()

    async def clean(self):
        await self.testrun_controller.clean()
        self.tanks[MEASURING_TANK].drain_tank()
        self.logger.debug("Draining measuring tank.")

        # set fill countdown to False
        for tank in self.tanks.values():
            tank.state = "STOPPED"

        # shutdown pumps
        for pump in self.pumps.values():
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
            await self.testrun_controller.start_run()

        while not self._app_control.is_terminating():
            await asyncio.sleep(1)

        self.logger.debug("Vosekast stopped.")

    # all devices publish their state via mqtt
    def state_overview(self):
        for device in (
            self.tanks.values()
            + self.pumps.values()
            + self.valves.values()
            + self.level_sensors.values()
        ):
            device.publish_state()

    # handle incoming mqtt commands
    async def handle_command(self, command):
        target = command.get("target")
        target_id = command.get("target_id")
        command_id = command.get("command")
        data = command.get("data")

        if target == "valve":
            self.handle_valve_command(target_id, command_id)
        elif target == "pump":
            self.handle_pump_command(target_id, command_id)
        elif target == "tank":
            self.handle_tank_command(target_id, command_id)
        elif target == "scale":
            self.handle_scale_command(command_id)
        elif target == "system":
            await self.handle_system_command(command_id, data)
        else:
            self.logger.warning(f"command target {target} unknown.")

    def handle_valve_commands(self, valve_id: str, command_id: str):
        valve = self.valves.get(valve_id)

        if valve is None:
            self.logger.warning(f"target_id {valve_id} unknown.")
            return

        if command_id == "close":
            self.valve.close()
            return
        elif command_id == "open":
            self.valve.open()
            return
        else:
            self.logger.warning(
                f"Received unknown command {command_id} for \
                target_id {valve_id}."
            )

        return

    def handle_pump_command(self, pump_id: str, command_id: str):
        pump = self.pumps.get(pump_id)

        if pump is None:
            self.logger.warning(f"Pump with id {pump_id} unknown.")
            return

        if command_id == "start":
            pump.start()
        elif command_id == "stop":
            pump.stop()
        elif command_id == "toggle":
            pump.toggle()
        else:
            self.logger.warning(
                f"Received unknown command {command_id} for \
                target_id {pump_id}."
            )

    def handle_tank_command(self, tank_id: str, command_id: str):
        tank = self.tanks.get(tank_id)

        if tank is None:
            self.logger.warning(f"Tank with id {tank_id} unknown.")

        if command_id == "drain_tank":
            tank.drain_tank()
        elif command_id == "prepare_to_fill":
            tank.prepare_to_fill()
        else:
            self.logger.warning(
                f"Received unknown command {command_id} for \
                tank {tank_id}."
            )

    def handle_scale_command(self, command_id: str):
        scale = self.scale

        if self.scale is None:
            self.logger.warning(f"No scale for command {command_id} registered!")

        if command_id == "open_connection":
            scale.open_connection()
        elif command_id == "close_connection":
            scale.close_connection()
        elif command_id == "start_measurement_thread":
            scale.start_measurement_thread()
        elif command_id == "stop_measurement_thread":
            scale.stop_measurement_thread()
        elif command_id == "print_diagnostics":
            scale.print_diagnostics()
        else:
            self.logger.warning(
                f"Received unknown command {command_id} for \
                    scale."
            )

    async def handle_system_command(self, command_id: str, data: Dict[str, str]):
        if command_id == "shutdown":
            await self.shutdown()
        elif command_id == "prepare_measuring":
            self.prepare_measuring()
        elif command_id == "start_run":
            await self.testrun_controller.start_run()
        elif command_id == "stop_current_run":
            await self.testrun_controller.stop_run()
        elif command_id == "pause_current_run":
            self.testrun_controller.pause_run()
        elif command_id == "empty_tanks":
            await self.empty_tanks()
        elif command_id == "state_overview":
            self.state_overview()
        elif command_id == "get_test_results":
            run_id = data.get("run_id")
            data = self.testrun_controller.get_testresults(run_id=data.get("run_id"))
            MQTTConnection.publish_message(DataMessage("test_results", run_id, data))
        elif command_id == "get_current_run":
            infos = self.testrun_controller.get_current_run_infos()
            MQTTConnection.publish_message(InfoMessage("testrun_controller", infos))
        else:
            self.logger.warning(
                f"Received unknown command {command_id} for \
                    system."
            )


class NoGPIOControllerError(Exception):
    pass
