import logging
from lib.Log import LOGGER
import asyncio
from lib.utils.Msg import StatusMessage


class Tank():
    # tank states
    UNKNOWN = -1
    DRAINED = -0.1
    EMPTY = 0
    FILLED = 1
    BETWEEN = 0.5

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
        self.progress = None
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
            self.progress = self.IS_DRAINING
        else:
            self.logger.warning(
                "No valve to drain the tank {}".format(self.name))

    def prepare_to_fill(self):
        if self.drain_valve is not None:
            self.drain_valve.close()
        else:
            self.logger.debug(
                "No drain valve on the tank {}".format(self.name))
            mqttmsg = StatusMessage(self.name, 'Drain valve missing.')
            self.mqtt.publish_message(mqttmsg)
        self.logger.info("Ready to fill the tank {}".format(self.name))

        mqttmsg = StatusMessage(
            self.name, 'Ready to fill the tank.', unit=None)
        self.mqtt.publish_message(mqttmsg)

    async def _up_state_changed(self, pin, alert):
        if alert:
            self._tank_is_full()
        else:
            self._tank_get_drained()

    def _tank_get_drained(self):
        """
        internal function to register that the tank gets drained from highest position
        :return:
        """
        self.state = self.BETWEEN
        mqttmsg = StatusMessage(self.name, 'DRAINING', unit=None)

        self.logger.info("Tank {} is being drained.".format(self.name))
        self.mqtt.publish_message(mqttmsg)

        # if self.gui_element is not None:
        #    self.state_changed.emit(self.BETWEEN)

    def _tank_is_full(self):
        """
        internal function to register that the tank is filled
        :return:
        """
        self.state = self.FILLED
        mqttmsg = StatusMessage(self.name, 'FULL', unit=None)

        self.logger.warning("Tank {} is full.".format(self.name))
        self.mqtt.publish_message(mqttmsg)

        # if self.gui_element is not None:
        #    self.state_changed.emit(self.FILLED)

        if self.source_pump is not None and self.protect_overflow:
            self.source_pump.stop()

    async def _low_position_changed(self, pin, alert):
        if alert:
            self._tank_is_drained()
        else:
            self._tank_get_filled()

    def _tank_get_filled(self):
        """
        internal function to register that the tank gets filled
        :return:
        """
        self.state = self.BETWEEN
        mqttmsg = StatusMessage(self.name, 'FILLING', unit=None)

        self.logger.warning("Tank {} is being filled".format(self.name))
        self.mqtt.publish_message(mqttmsg)

        # if self.gui_element is not None:
        #    self.state_changed.emit(self.BETWEEN)

    def _tank_is_drained(self):
        """
        internal function to register that the tank is drained
        :return:
        """
        self.state = self.DRAINED
        mqttmsg = StatusMessage(self.name, 'DRAINED', unit=None)

        self.logger.warning("Tank {} is drained".format(self.name))
        self.mqtt.publish_message(mqttmsg)

        # if self.gui_element is not None:
        #    self.state_changed.emit(self.DRAINED)

        if self.drain_valve is not None and self.protect_draining:
            self.drain_valve.close()
