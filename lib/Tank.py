import logging
from lib.Log import LOGGER


class Tank:
    UNKNOWN = 'UNKNOWN'
    DRAINED = 'DRAINED'
    IS_DRAINING = 'IS_DRAINING'
    FILLED = 'FILLED'
    IS_FILLING = 'IS_FILLED'

    def __init__(self,
                 name,
                 capacity,
                 level_sensor,
                 drain_sensor,
                 overflow_sensor,
                 drain_valve,
                 source_pump,
                 protect_draining=True,
                 protect_overflow=True):

        self.name = name
        self.capacity = capacity
        self.level_sensor = level_sensor
        self.drain_sensor = drain_sensor
        self.overflow_sensor = overflow_sensor
        self.drain_valve = drain_valve
        self.source_pump = source_pump
        self.state = self.UNKNOWN
        self.logger = logging.getLogger(LOGGER)
        self.protect_draining = protect_draining
        self.protect_overflow = protect_overflow

        self.level = None

        # register callback for overfill if necessary
        if overflow_sensor is not None:
            self.overflow_sensor.add_callback(self._tank_is_full)

        if drain_sensor is not None:
            self.drain_sensor.add_callback(self._tank_is_empty)

    def drain_tank(self):
        if self.drain_valve is not None:
            self.drain_valve.open()
            self.state = self.IS_DRAINING
        else:
            self.logger.warning(F"No valve to drain the tank {self.name}")

    def prepare_to_fill(self):
        if self.drain_valve is not None:
            self.drain_valve.close()
        else:
            self.logger.debug(F"No drain valve on the tank {self.name}")
        self.logger.info(F"Ready to fill the tank {self.name}")

    def _tank_is_full(self, pin):
        """
        intern function to register that the tank is filled
        :return:
        """
        self.state = self.FILLED
        self.logger.warning(F"Tank {self.name} is filled.")
        if self.source_pump is not None and self.protect_overflow:
            self.source_pump.stop()

    def _tank_is_empty(self, pin):
        """
        intern function to register that the tank is drained
        :return:
        """
        self.state = self.DRAINED
        self.logger.warning(F"Tank {self.name} is drained")
        if self.drain_valve is not None and self.protect_draining:
            self.drain_valve.close()
