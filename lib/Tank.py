import logging
from lib.Log import LOGGER


class Tank:
    UNKNOWN = 'UNKNOWN'
    DRAINED = 'DRAINED'
    IS_DRAINING = 'IS_DRAINING'
    FILLED = 'FILLED'
    IS_FILLING = 'IS_FILLED'

    def __init__(self, name, capacity, level_sensor, drain_sensor, overflow_sensor, drain_valve):
        self.name = name
        self.capacity = capacity
        self.level_sensor = level_sensor
        self.drain_sensor = drain_sensor
        self.overflow_sensor = overflow_sensor
        self.drain_valve = drain_valve
        self.state = self.UNKNOWN
        self.logger = logging.getLogger(LOGGER)

        self.level = None

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
