import logging
from vosekast_control.Log import LOGGER
import asyncio
from vosekast_control.utils.Msg import StatusMessage
from datetime import datetime

class TankFillingTimeout(Exception):
    pass

class Tank():
    # tank states
    UNKNOWN = -1
    DRAINED = -0.1
    EMPTY = 0
    FILLED = 1
    BETWEEN = 0.5
    STOPPED = 3

    IS_DRAINING = "IS_DRAINING"
    IS_FILLING = "IS_FILLED"

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
        self.state = self.UNKNOWN
        self.logger = logging.getLogger(LOGGER)
        self.protect_draining = protect_draining
        self.protect_overflow = protect_overflow
        self.mqtt = self.vosekast.mqtt_client

        # register callback for overfill if necessary
        if overflow_sensor is not None:
            self.overflow_sensor.add_callback(self._up_state_changed)

        if drain_sensor is not None:
            self.drain_sensor.add_callback(self._low_position_changed)

    def drain_tank(self):
        if self.drain_valve is not None:
            self.drain_valve.open()
            self.state = self.IS_DRAINING
        else:
            self.logger.warning(
                "No valve to drain the tank {}".format(self.name))

    def prepare_to_fill(self):
        if self.drain_valve is not None:
            self.drain_valve.close()
        else:
            self.logger.debug(
                "No drain valve on the {}".format(self.name))
            return
        self.logger.info("Ready to fill the tank {}".format(self.name))

    async def _up_state_changed(self, pin, alert):
        if alert:
            self._on_full()
        else:
            self._on_draining()

    async def fill(self):
        print("Measuring Tank filled: " + str(self.vosekast.measuring_tank.is_filled))

        if not self.vosekast.constant_tank.is_filled:
            try:
                #get time
                time_filling_t0 = datetime.now()
                #close valves, start pump
                self.vosekast.prepare_measuring()
                self.state = self.BETWEEN
                
                #check if constant_tank full
                while not self.vosekast.constant_tank.is_filled and self.fill_state == True:

                    time_filling_t1 = datetime.now()
                    time_filling_passed = time_filling_t1 - time_filling_t0
                    delta_time_filling = time_filling_passed.total_seconds()
                    
                    #if filling takes longer than 90s
                    if delta_time_filling >= 90:
                        self.logger.error(
                        "Filling takes too long. Please make sure that all valves are closed and the pump is working. Aborting.")
                        raise TankFillingTimeout("Tank Filling Timeout.")
                    
                    self.logger.debug(str(delta_time_filling) + 's < time allotted (90s)')
                    await asyncio.sleep(1)
                
                return
            except:
                self.stop_fill
                self.logger.info("Filling {} aborted.".format(self.name))
                return
        else:
            self.logger.info("{} already filled. Continuing.".format(self.name))
    


    @property
    def start_fill(self):
        self.fill_state = True

    @property
    def stop_fill(self):
        self.fill_state = False

    def _on_draining(self):
        """
        internal function to register that the tank gets drained from highest position
        :return:
        """
        self.state = self.BETWEEN

        self.logger.info("{} is being drained.".format(self.name))

    def _on_full(self):
        """
        internal function to register that the tank is filled
        :return:
        """
        self.state = self.FILLED

        self.logger.info("{} is full.".format(self.name))

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
        self.state = self.BETWEEN

        self.logger.info("{} is being filled".format(self.name))

    def _handle_drained(self):
        """
        internal function to register that the tank is drained
        :return:
        """
        self.state = self.DRAINED

        self.logger.info("{} is drained".format(self.name))

        if self.drain_valve is not None and self.protect_draining:
            self.drain_valve.close()

    @property
    def is_filled(self):
        return self.state == self.FILLED

    @property
    def is_drained(self):
        return self.state == self.DRAINED    
