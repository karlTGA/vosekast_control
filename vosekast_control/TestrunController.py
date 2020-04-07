import logging
import asyncio
from vosekast_control.Log import LOGGER
from vosekast_control.utils.Constants import (
    MEASURING_TANK,
    PUMP_MEASURING_TANK,
    MEASURING_TANK_SWITCH,
    CONSTANT_TANK,
)
from typing import Optional
from vosekast_control.connectors.MQTTConnector import MQTTConnection
from vosekast_control.utils.Msg import StatusMessage
from vosekast_control.Testrun import Testrun
from vosekast_control.connectors import DBConnection


class TestrunController:
    # TestSequence states
    INITED = "INITED"
    WAITING = "WAITING"
    MEASURING = "MEASURING"
    PAUSED = "PAUSED"
    STOPPED = "STOPPED"

    def __init__(self, vosekast, options={}):

        super().__init__()
        self.logger = logging.getLogger(LOGGER)
        self.vosekast = vosekast
        self.valves = self.vosekast.valves
        self.tank = self.vosekast.tanks
        self.pumps = self.vosekast.pumps
        self.scale = self.vosekast.scale
        self.emulate = options.get("emulate", False)
        self._state = self.INITED
        self.current_run = None

    async def start_run(self):
        if self.state == self.WAITING or self.state == self.MEASURING:
            self.logger.info("Already measuring.")
            return

        try:
            self.logger.info("Initialising test run.")
            self.current_run = Testrun(vosekast=self.vosekast)
            self.current_run.publish_infos()

            # change state
            self.state = self.WAITING

            # check if already running
            # remove the scale start. Scale should running. Testsequenze can test that, not more.
            if not self.scale.is_running:
                self.scale.start()
                self.logger.info(
                    "Initialising scale connection & measurement thread. Please wait."
                )
                await asyncio.sleep(1)

            # only fill if not already full
            # todo: combine that to an test sequenze
            # todo: test sequnce should not change state of tank
            if (
                not self.vosekast.tanks[CONSTANT_TANK].state
                == self.vosekast.tanks[CONSTANT_TANK].FILLED
            ):
                self.vosekast.tanks[CONSTANT_TANK].state = self.vosekast.tanks[
                    CONSTANT_TANK
                ].IS_FILLING
                # await constant_tank full
                await self.vosekast.tanks[CONSTANT_TANK].fill()
            else:
                self.vosekast.prepare_measuring()

            # check ready_to_measure
            # todo add to test sequence
            if not self.vosekast.ready_to_measure:
                self.logger.debug("Vosekast not ready to measure.")
                self.scale.print_diagnostics()
                self.state = self.STOPPED
                return

            # check if state has been changed
            # that should not possible, check all state changes
            elif self.state == self.STOPPED or self.state == self.PAUSED:
                return

            self.logger.debug("Vosekast ready to measure.")
            # turn on measuring pump, start measuring
            await self._start_measurement()

            self.vosekast.state = self.vosekast.MEASURING
            self.state = self.MEASURING

            # write to file
            await self.current_run.start()

        finally:
            await self.stop_current_run()
            self.vosekast.tanks[CONSTANT_TANK].state = self.vosekast.tanks[
                CONSTANT_TANK
            ].STOPPED
            self.vosekast.state = self.vosekast.RUNNING

    async def _start_measurement(self):
        try:
            self.vosekast.tanks[MEASURING_TANK].prepare_to_fill()
            self.vosekast.valves[MEASURING_TANK_SWITCH].close()
            self.vosekast.pumps[PUMP_MEASURING_TANK].start()
            self.logger.debug("Measuring Pump spin up. Please wait.")

            await asyncio.sleep(2)

            self.vosekast.valves[MEASURING_TANK_SWITCH].open()
            self.logger.debug("Measuring started.")

        except Exception:
            self.logger.debug("Measuring aborted.")
            self.vosekast.pumps[PUMP_MEASURING_TANK].stop()
            self.vosekast.state = self.vosekast.RUNNING
            raise

    async def stop_current_run(self):
        if (
            self.state == self.MEASURING
            or self.state == self.PAUSED
            or self.state == self.WAITING
        ):
            self.state = self.STOPPED
            self.vosekast.valves[MEASURING_TANK_SWITCH].close()
            self.logger.debug("Stopped test sequence")
            self.vosekast.state = self.vosekast.RUNNING
            self.current_run.stop()
            del self.current_run

            await self.vosekast.clean()
        else:
            self.logger.info("Sequence has not yet been started.")

    def pause_current_run(self):
        if self.state == self.MEASURING:
            self.current_run.pause()

            # set fill countdown to False
            self.vosekast.tanks[CONSTANT_TANK].state = self.vosekast.tanks[
                CONSTANT_TANK
            ].PAUSED

            # switch to measuring_tank bypass
            self.vosekast.valves[MEASURING_TANK_SWITCH].close()

            self.logger.info("Paused. Measuring Tank bypass open.")

        # if constant_tank has not been filled yet
        elif self.state == self.WAITING and self.vosekast.PREPARING_MEASUREMENT:
            self.state = self.STOPPED
            self.vosekast.state = self.vosekast.RUNNING
            self.logger.info(
                "Measuring has not yet started, continuing to fill constant_tank."
            )
        elif self.state == self.PAUSED or self.state == self.STOPPED:
            self.logger.info("Sequence already paused.")
        else:
            self.logger.info("Sequence has not yet been started.")

    async def continue_current_run(self):
        if self.state == self.PAUSED:
            self.state = self.MEASURING

            # set fill countdown to True
            self.vosekast.tanks[CONSTANT_TANK].state = self.vosekast.tanks[
                CONSTANT_TANK
            ].IS_FILLING

            self.vosekast.valves[MEASURING_TANK_SWITCH].open()
            self.logger.info("Continuing. Measuring Tank is being filled.")
            await self.write_loop()
        elif self.state == self.WAITING or self.state == self.MEASURING:
            self.logger.info("Sequence has not been paused.")
        else:
            self.logger.info("Sequence has not yet been started.")

    def publish_current_run_infos(self):
        if self.current_run is not None:
            self.current_run.publish_infos()

    def get_testresults(self, run_id: Optional[str] = None):
        if run_id is None:
            run_id = self.current_run.id

        return DBConnection.get_run_data(run_id=run_id)

    async def clean(self):
        await self.stop_current_run()

    def publish_state(self):
        MQTTConnection.publish_message(
            StatusMessage(
                "system",
                "testrun_controller",
                self.state,
                properties={"run_id": self.current_run.id},
            )
        )

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        self._state = new_state
        self.publish_state()
