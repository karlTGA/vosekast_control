import logging
from lib.Log import LOGGER
from PyQt5.QtCore import pyqtSignal, QObject


class Tank(QObject):
    # tank states
    UNKNOWN = -1
    DRAINED = 0
    FILLED = 1

    IS_DRAINING = 'IS_DRAINING'
    IS_FILLING = 'IS_FILLED'

    # signals
    state_changed = pyqtSignal(float, name="TankStateChange")

    def __init__(self,
                 name,
                 capacity,
                 level_sensor,
                 drain_sensor,
                 overflow_sensor,
                 drain_valve,
                 source_pump,
                 gui_element,
                 protect_draining=True,
                 protect_overflow=True):

        super().__init__()
        self.name = name
        self.capacity = capacity
        self.level_sensor = level_sensor
        self.drain_sensor = drain_sensor
        self.overflow_sensor = overflow_sensor
        self.drain_valve = drain_valve
        self.source_pump = source_pump
        self.state = self.UNKNOWN
        self.progress = None
        self.logger = logging.getLogger(LOGGER)
        self.protect_draining = protect_draining
        self.protect_overflow = protect_overflow
        self.gui_element = gui_element

        # register callback for overfill if necessary
        if overflow_sensor is not None:
            self.overflow_sensor.add_callback(self._tank_is_full)

        if drain_sensor is not None:
            self.drain_sensor.add_callback(self._tank_is_empty)

        # signals for gui
        if gui_element is not None:
            self.state_changed.connect(self.gui_element.state_change)

    def drain_tank(self):
        if self.drain_valve is not None:
            self.drain_valve.open()
            self.progress = self.IS_DRAINING
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

        if self.gui_element is not None:
            self.state_changed.emit(self.FILLED)
        
        if self.source_pump is not None and self.protect_overflow:
            self.source_pump.stop()

    def _tank_is_empty(self, pin):
        """
        intern function to register that the tank is drained
        :return:
        """
        self.state = self.DRAINED
        self.logger.warning(F"Tank {self.name} is drained")

        if self.gui_element is not None:
            self.state_changed.emit(self.DRAINED)

        if self.drain_valve is not None and self.protect_draining:
            self.drain_valve.close()
