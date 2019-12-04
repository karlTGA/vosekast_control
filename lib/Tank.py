import logging
from lib.Log import LOGGER
from PyQt5.QtCore import pyqtSignal, QObject


class Tank(QObject):
    # tank states
    UNKNOWN = -1
    DRAINED = -0.1
    EMPTY = 0
    FILLED = 1
    BETWEEN = 0.5

    IS_DRAINING = "IS_DRAINING"
    IS_FILLING = "IS_FILLED"

    # signals
    state_changed = pyqtSignal(float, name="TankStateChange")

    def __init__(
        self,
        name,
        capacity,
        level_sensor,
        drain_sensor,
        overflow_sensor,
        drain_valve,
        source_pump,
        gui_element,
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
        self.state = self.UNKNOWN
        self.progress = None
        self.logger = logging.getLogger(LOGGER)
        self.protect_draining = protect_draining
        self.protect_overflow = protect_overflow
        self.gui_element = gui_element

        # register callback for overfill if necessary
        if overflow_sensor is not None:
            self.overflow_sensor.add_callback(self._up_state_changed)

        if drain_sensor is not None:
            self.drain_sensor.add_callback(self._low_position_changed)

        # signals for gui
        if gui_element is not None:
            self.state_changed.connect(self.gui_element.state_change)

    def drain_tank(self):
        if self.drain_valve is not None:
            self.drain_valve.open()
            self.progress = self.IS_DRAINING
        else:
            self.logger.warning("No valve to drain the tank {}".format(self.name))

    def prepare_to_fill(self):
        if self.drain_valve is not None:
            self.drain_valve.close()
        else:
            self.logger.debug("No drain valve on the tank {}".format(self.name))
        self.logger.info("Ready to fill the tank {}".format(self.name))

    def _up_state_changed(self, pin, alert):
        if alert:
            self._tank_is_full()
        else:
            self._tank_get_drained()

    def _tank_get_drained(self):
        """
        intern function to register that the tank get drained from highest position
        :return:
        """
        self.state = self.BETWEEN
        self.logger.info("Tank {} get drained.".format(self.name))

        if self.gui_element is not None:
            self.state_changed.emit(self.BETWEEN)

    def _tank_is_full(self):
        """
        intern function to register that the tank is filled
        :return:
        """
        self.state = self.FILLED
        self.logger.warning("Tank {} is filled.".format(self.name))

        if self.gui_element is not None:
            self.state_changed.emit(self.FILLED)

        if self.source_pump is not None and self.protect_overflow:
            self.source_pump.stop()

    def _low_position_changed(self, pin, alert):
        if alert:
            self._tank_is_drained()
        else:
            self._tank_get_filled()

    def _tank_get_filled(self):
        """
        intern function to register that the tank get filled
        :return:
        """
        self.state = self.BETWEEN
        self.logger.warning("Tank {} get filled".format(self.name))

        if self.gui_element is not None:
            self.state_changed.emit(self.BETWEEN)

    def _tank_is_drained(self):
        """
        intern function to register that the tank is drained
        :return:
        """
        self.state = self.DRAINED
        self.logger.warning("Tank {} is drained".format(self.name))

        if self.gui_element is not None:
            self.state_changed.emit(self.DRAINED)

        if self.drain_valve is not None and self.protect_draining:
            self.drain_valve.close()
