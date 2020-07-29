import logging
import asyncio
from vosekast_control.Log import LOGGER
from vosekast_control.utils.Msg import StatusMessage
from datetime import datetime

from vosekast_control.connectors import MQTTConnection
from vosekast_control.utils.Constants import MEASURING_TANK, CONSTANT_TANK


class TankFillingTimeout(Exception):
    pass


class Tank:
    # tank states
    UNKNOWN = "UNKNOWN"
    DRAINED = "DRAINED"
    EMPTY = "EMPTY"
    FILLED = "FILLED"
    PAUSED = "PAUSED"
    STOPPED = "STOPPED"
    IS_DRAINING = "IS_DRAINING"
    IS_FILLING = "IS_FILLING"

    def __init__(
        self,
        name,
        capacity,
        level_sensor,
        drain_sensor,
        overflow_sensor,
        drain_valve,
        source_pump,
        vosekast,
        protect_draining=True,
        protect_overflow=True,
        emulate=False,
    ):

        super().__init__()
        self.name = name
        self.capacity = capacity
        self.level_sensor = level_sensor
        self.drain_sensor = drain_sensor
        self.overflow_sensor = overflow_sensor
        self.drain_valve = drain_valve
        self.source_pump = source_pump
        self.vosekast = vosekast
        self._state = self.UNKNOWN
        self.logger = logging.getLogger(LOGGER)
        self.protect_draining = protect_draining
        self.protect_overflow = protect_overflow
        self.emulate = emulate

        # register callback for overfill if necessary
        if overflow_sensor is not None:
            self.overflow_sensor.add_callback(self._up_state_changed)

        if drain_sensor is not None:
            self.drain_sensor.add_callback(self._low_position_changed)

    def stop_filling(self):
        if self.source_pump is not None:
            self.source_pump.stop()

        self.state = self.STOPPED

    def drain_tank(self):
        if self.drain_valve is None:
            self.logger.warning("No valve to drain the tank {}".format(self.name))
            return

        self.drain_valve.open()
        self._state = self.IS_DRAINING

    def prepare_to_fill(self):
        if self.drain_valve is None:
            self.logger.debug("No drain valve on the {}".format(self.name))
            return

        self.drain_valve.close()
        self.logger.info("Ready to fill the tank {}".format(self.name))

    async def _up_state_changed(self, pin, alert):
        if alert:
            self._on_full()
        else:
            self._on_draining()

    async def fill(self, keep_source_active=False, max_filling_time=75):
        if self._state == self.FILLED:
            self.logger.info(f"{self.name} already filled. Continuing.")
            return

        if self.emulate:
            self.logger.info(
                f"Fill the tank {self.name} im emulate mode. Wait 10 seconds."
            )
            self.source_pump.start()
            await asyncio.sleep(10)
            self._on_full()
            return

        try:
            # get time
            start_filling_time = datetime.now()

            # close valves, start pump
            self.prepare_to_fill()
            self.source_pump.start()
            self._state = self.IS_FILLING

            # check if constant_tank full
            while not self._state == self.FILLED and self._state == self.IS_FILLING:
                delta_time_filling = (
                    datetime.now() - start_filling_time
                ).total_seconds()

                # if filling takes longer than max_filling_time in sek
                if delta_time_filling >= max_filling_time:
                    self.logger.error(
                        "Filling takes too long. Please make sure that all valves are closed and the pump is working. Aborting."
                    )
                    raise TankFillingTimeout("Tank Filling Timeout.")

                await asyncio.sleep(1)

            self.logger.info(f"Filled the tank {self.name}.")

            if not keep_source_active:
                self.source_pump.stop()

            return

        except Exception:
            self.drain_tank()
            self.logger.error(
                f"Exception by filling the tank {self.name}. Aborted the process and init draining."
            )
            raise

    def _on_draining(self):
        """
        internal function to register that the tank gets drained from highest position
        :return:
        """
        self._state = self.IS_DRAINING

    def _on_full(self):
        """
        internal function to register that the tank is filled
        :return:
        """
        self._state = self.FILLED

        if self.source_pump is not None and self.protect_overflow:
            self.source_pump.stop()

    async def _low_position_changed(self, pin, alert):
        if alert:
            self._handle_drained()
        else:
            self._handle_filling()

    def _handle_filling(self):
        """
        internal function to register that the tank gets filled
        :return:
        """
        self._state = self.IS_FILLING

    def _handle_drained(self):
        """
        internal function to register that the tank is drained
        :return:
        """
        self._state = self.DRAINED

        if self.drain_valve is not None and self.protect_draining:
            self.drain_valve.close()

    @property
    def is_filled(self):
        return self._state == self.FILLED

    @property
    def is_drained(self):
        return self._state == self.DRAINED

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        self._state = new_state
        self.logger.info(f"New {self.name} state is: {new_state}")
        self.publish_state()

    def publish_state(self):
        MQTTConnection.publish_message(StatusMessage("tank", self.name, self.state))
