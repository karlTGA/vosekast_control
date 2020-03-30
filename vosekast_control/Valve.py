import logging
from vosekast_control.Log import LOGGER
from vosekast_control.utils.Msg import StatusMessage

from vosekast_control.connectors import MQTTConnection


class Valve:
    # regulations
    BINARY = "BINARY"
    ANALOG = "ANALOG"

    # valve_types
    TWO_WAY = "TWO_WAY"
    THREE_WAY = "THREE_WAY"
    SWITCH = "SWITCH"

    # valve states
    UNKNOWN = "UNKNOWN"
    OPEN = "OPEN"
    CLOSED = "CLOSED"

    def __init__(
        self, vosekast, name, control_pin, valve_type, regulation, gpio_controller,
    ):
        super().__init__()

        self.vosekast = vosekast
        self.name = name
        self._pin = control_pin
        self.valve_type = valve_type
        self.regulation = regulation
        self._gpio_controller = gpio_controller
        self._state = self.UNKNOWN
        self.logger = logging.getLogger(LOGGER)
        self.state = self.UNKNOWN

        # init the gpio pin
        self._gpio_controller.setup(self._pin, self._gpio_controller.OUT)

    # todo bounce
    def close(self):
        """
        function to close the valve or switch
        :return:
        """
        self.logger.info("Closing {}".format(self.name))

        # todo this triggers bounce
        self._gpio_controller.output(self._pin, self._gpio_controller.LOW)

        self.state = self.CLOSED

    def open(self):
        """
        open the valve
        :return:
        """
        self.logger.info("Opening {}".format(self.name))

        # todo this triggers bounce
        self._gpio_controller.output(self._pin, self._gpio_controller.HIGH)

        self.state = self.OPEN

    @property
    def is_closed(self):
        return self.state == self.CLOSED

    @property
    def is_open(self):
        return self.state == self.OPEN

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        self._state = new_state
        self.logger.info(f"New state of valve {self.name} is: {new_state}")
        self.publish_state()

    def publish_state(self):
        MQTTConnection.publish_message(StatusMessage("valve", self.name, self.state))
