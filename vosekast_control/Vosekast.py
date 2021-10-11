from vosekast_control.Pump import Pump
from vosekast_control.Tank import Tank
from vosekast_control.LevelSensor import LevelSensor
from vosekast_control.Valve import Valve
from vosekast_control.Scale import Scale
from vosekast_control.TestrunController import TestrunController

from typing import Dict
import itertools
import logging
import asyncio
from vosekast_control.Log import LOGGER, add_mqtt_logger_handler

from vosekast_control.connectors import MQTTConnection
from vosekast_control.connectors import AppControl
from vosekast_control.utils.Msg import DataMessage, StatusMessage
from vosekast_control.connectors.DBConnector import DBConnection
from vosekast_control.utils.Constants import (
    MEASURING_BYPASS_VALVE,
    RELAY_PORT_VALVE_MEASURING_BYPASS,
    SCALE_MEASURING,
    MEASURING_DRAIN_VALVE,
    RELAY_PORT_VALVE_MEASURING_FILL,
    RELAY_PORT_VALVE_MEASURING_DRAIN,
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
    RELAY_PORT_PUMP_CONSTANT,
    RELAY_PORT_PUMP_MEASURING,
    CONSTANT_TANK,
    STOCK_TANK,
    MEASURING_TANK,
)

logger = logging.getLogger(LOGGER)


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

    def __init__(self, gpio_controller, emulate=False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.emulate = emulate
        self._event_loop = asyncio.get_event_loop()

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
            self.scale = Scale(name=SCALE_MEASURING, emulate=self.emulate)

            self.testrun_controller = TestrunController(vosekast=self)

            # change state if ok
            self._state = self.INITED

        except NoGPIOControllerError:
            logger.error(
                "You have to add a gpio controller to control or simulate the components."
            )

    def _init_valves(self):
        measuring_drain_valve = Valve(
            self,
            MEASURING_DRAIN_VALVE,
            RELAY_PORT_VALVE_MEASURING_DRAIN,
            Valve.SWITCH,
            Valve.BINARY,
        )
        measuring_tank_switch = Valve(
            self,
            MEASURING_TANK_SWITCH,
            RELAY_PORT_VALVE_MEASURING_FILL,
            Valve.SWITCH,
            Valve.BINARY,
        )
        measuring_bypass_valve = Valve(
            self,
            MEASURING_BYPASS_VALVE,
            RELAY_PORT_VALVE_MEASURING_BYPASS,
            Valve.SWITCH,
            Valve.BINARY,
        )
        
        self.valves = {
            MEASURING_DRAIN_VALVE: measuring_drain_valve,
            MEASURING_BYPASS_VALVE: measuring_bypass_valve,
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
        pump_constant_tank = Pump(self, PUMP_CONSTANT_TANK, RELAY_PORT_PUMP_CONSTANT,)
        pump_measuring_tank = Pump(
            self, PUMP_MEASURING_TANK, RELAY_PORT_PUMP_MEASURING,
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

    async def prepare_measuring(self):
        """
        before we can measure we have to prepare the station
        :return:
        """
        # close MDV,
        # fill the constant tank, start the measurement pumps.
        self.valves[MEASURING_DRAIN_VALVE].close()
        await self.tanks[CONSTANT_TANK].fill(keep_source_active=True)
        self.pumps[PUMP_MEASURING_TANK].stop()
        self.scale.start()

        self._state = self.PREPARING_MEASUREMENT

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        self._state = new_state
        logger.debug(f"New Vosekast state is: {new_state}")

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
        logger.warning(
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
        logger.info("Shutting down.")

        await MQTTConnection.disconnect()
        logger.debug("MQTT client disconnected.")

        AppControl.shutdown()

    async def clean(self):
        await self.testrun_controller.clean()
        self.tanks[MEASURING_TANK].drain_tank()
        logger.debug("Draining measuring tank.")

        # set fill countdown to False
        for tank in self.tanks.values():
            tank.state = "STOPPED"

        # shutdown pumps
        for pump in self.pumps.values():
            pump.stop()

        logger.debug("All pumps switched off.")

        # stop scale
        logger.debug("Now stopping scale.")
        await self.scale.stop()

    async def run(self):
        if self.emulate:
            logger.info("Start Vosekast in Debug Mode.")

        self.scale.start()

        await MQTTConnection.connect()
        self._state = self.RUNNING
        logger.debug("Vosekast started ok.")

        while not AppControl.is_terminating():
            await asyncio.sleep(1)

        logger.debug("Vosekast stopped.")

    # all devices publish their state via mqtt
    def state_overview(self):
        for device in itertools.chain(
            self.tanks.values(),
            self.pumps.values(),
            self.valves.values(),
            self.level_sensors.values(),
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
            logger.warning(f"command target {target} unknown.")

    def handle_valve_command(self, valve_id: str, command_id: str):
        valve = self.valves.get(valve_id)

        if valve is None:
            logger.warning(f"target_id {valve_id} unknown.")
            return

        if command_id == "close":
            valve.close()
            return
        elif command_id == "open":
            valve.open()
            return
        else:
            logger.warning(
                f"Received unknown command {command_id} for \
                target_id {valve_id}."
            )

        return

    def handle_pump_command(self, pump_id: str, command_id: str):
        pump = self.pumps.get(pump_id)

        if pump is None:
            logger.warning(f"Pump with id {pump_id} unknown.")
            return

        if command_id == "start":
            pump.start()
        elif command_id == "stop":
            pump.stop()
        elif command_id == "toggle":
            pump.toggle()
        else:
            logger.warning(
                f"Received unknown command {command_id} for \
                target_id {pump_id}."
            )

    def handle_tank_command(self, tank_id: str, command_id: str):
        tank = self.tanks.get(tank_id)

        if tank is None:
            logger.warning(f"Tank with id {tank_id} unknown.")

        if command_id == "drain_tank":
            tank.drain_tank()
        elif command_id == "prepare_to_fill":
            tank.prepare_to_fill()
        else:
            logger.warning(
                f"Received unknown command {command_id} for \
                tank {tank_id}."
            )

    def handle_scale_command(self, command_id: str):
        scale = self.scale

        if self.scale is None:
            logger.warning(f"No scale for command {command_id} registered!")

        if command_id == "tare":
            scale.tare()
        elif command_id == "unlock_keys":
            scale.unlock_keys()
        elif command_id == "lock_keys":
            scale.lock_keys()
        elif command_id == "start":
            scale.start()
        elif command_id == "stop":
            self._event_loop.create_task(scale.stop())
        else:
            logger.warning(
                f"Received unknown command {command_id} for \
                    scale."
            )

    async def handle_system_command(self, command_id: str, data: Dict[str, str] = {}):
        if command_id == "shutdown":
            await self.shutdown()
        elif command_id == "prepare_measuring":
            await self.prepare_measuring()
        elif command_id == "start_run":
            await self.testrun_controller.start_run()
        elif command_id == "stop_current_run":
            await self.testrun_controller.stop_current_run()
        elif command_id == "pause_current_run":
            self.testrun_controller.pause_current_run()
        elif command_id == "empty_tanks":
            await self.empty_tanks()
        elif command_id == "state_overview":
            self.state_overview()
        elif command_id == "get_test_results":
            run_id = data.get("run_id")
            if run_id is None:
                logger.warn("Got test result request without run id.")
                return

            data = self.testrun_controller.get_testresults(run_id=data.get("run_id"))
            MQTTConnection.publish_message(DataMessage("test_results", run_id, data))
        elif command_id == "get_current_run_infos":
            self.testrun_controller.publish_current_run_infos()
        elif command_id == "get_run_ids":
            runIds = DBConnection.get_run_ids()
            MQTTConnection.publish_message(DataMessage("run_ids", "db", runIds))
        elif command_id == "request_current_app_state":
            MQTTConnection.publish_message(
                StatusMessage("system", "app_control", await AppControl.state)
            )
        else:
            logger.warning(
                f"Received unknown command {command_id} for \
                    system."
            )


class NoGPIOControllerError(Exception):
    pass
