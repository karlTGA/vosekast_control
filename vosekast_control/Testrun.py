from time import time
import logging
import random
import asyncio
from vosekast_control.utils.Constants import (
    MEASURING_TANK,
    MEASURING_TANK_SWITCH,
    PUMP_CONSTANT_TANK,
    MEASURING_DRAIN_VALVE,
    PUMP_MEASURING_TANK,
)
from vosekast_control.connectors.DBConnector import DBConnection
from vosekast_control.Log import LOGGER
from vosekast_control.connectors import MQTTConnection
from vosekast_control.utils.Msg import InfoMessage, DataMessage


class Testrun:
    MEASURING = "MEASURING"
    PAUSED = "PAUSED"
    STOPPED = "STOPPED"
    INITED = "INITED"

    created_at: int
    started_at: int
    ended_at: int
    emulate: bool
    id: str

    def __init__(self, vosekast, options={}):
        self.created_at = time()
        self.started_at = None
        self.ended_at = None
        self.emulate = options.get("emulate", False)
        self.id = str(random.randint(10000000000, 100000000000))
        self.vosekast = vosekast
        self.scale = vosekast.scale
        self.logger = logging.getLogger(LOGGER)
        self.scale_nulled = 0
        self.state = self.INITED
        self.publish_infos()

    async def _make_run(self):
        self.started_at = time()

        try:
            # tare scale
            # todo: to tare the scale should a method of the scale
            if abs(self.scale.scale_history[0]) < 0.15:
                self.scale_nulled = self.scale.scale_history[0]

            self.state = self.MEASURING
            self.publish_infos()

            # send values to db
            while (
                self.state == self.MEASURING
                and not self.vosekast.tanks[MEASURING_TANK].is_filled
            ):
                # emulate measuring_tank filled
                if self.emulate and time() - self.started_at <= 30:
                    self.vosekast.tanks[MEASURING_TANK].state = self.vosekast.tanks[
                        MEASURING_TANK
                    ].FILLED

                self._measure_value()
                await asyncio.sleep(1)

            # interrupt if measuring_tank full
            if self.vosekast.tanks[MEASURING_TANK].is_filled:
                self.vosekast.valves[MEASURING_TANK_SWITCH].close()
                self.vosekast.tanks[MEASURING_TANK].drain_tank()
                self.state = self.STOPPED
                self.logger.debug(
                    "Draining measuring tank, opening Measuring Tank bypass."
                )

        except Exception:
            self.logger.warning("Write loop killed, stopping sequence.")
            self.stop()
            raise

    async def start(self):
        await self._make_run()

    def pause(self):
        self.state = self.PAUSED
        self.publish_infos()

    def stop(self):
        self.state = self.STOPPED
        self.publish_infos()

    def publish_infos(self):
        MQTTConnection.publish_message(
            InfoMessage("testrun_controller", self.get_infos())
        )

    def _get_current_scale_value(self) -> float:
        if self.emulate:
            return round(self.scale.scale_history[0], 5)

        return round(self.scale.scale_history[0] - self.scale_nulled, 5)

    def _publish_new_value(self, datapoint):
        MQTTConnection.publish_message(
            DataMessage(data_type="test_result", identifier=self.id, payload=datapoint)
        )

    def _measure_value(self):
        # get the current value of the scale
        # todo: emulated or not should not interesting for the run class. the scale should
        # give a simple a value
        current_scale_value = self._get_current_scale_value()
        flow_average = self.scale.flow_average()

        data = {
            "timestamp": self.scale.scale_history[1],
            "scale_value": current_scale_value,
            "flow_current": self.scale.flow_history[0],
            "flow_average": flow_average,
            "pump_constant_tank_state": self.vosekast.pumps[PUMP_CONSTANT_TANK].state,
            "pump_measuring_tank_state": self.vosekast.pumps[PUMP_MEASURING_TANK].state,
            "measuring_drain_valve_state": self.vosekast.valves[
                MEASURING_DRAIN_VALVE
            ].state,
            "measuring_tank_switch_state": self.vosekast.valves[
                MEASURING_TANK_SWITCH
            ].state,
            "run_id": self.id,
        }
        self._publish_new_value(data)
        DBConnection.insert_datapoint(data)

        self.logger.debug(
            f"{current_scale_value} kg, flow rate (average) {flow_average} L/s"
        )

    def get_infos(self):
        return {
            "id": self.id,
            "startedAt": self.started_at,
            "createdAt": self.created_at,
            "state": self.state,
            "emulate": self.emulate,
        }
