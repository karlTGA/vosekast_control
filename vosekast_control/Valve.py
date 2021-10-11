import logging
from vosekast_control.Log import LOGGER
from vosekast_control.connectors.RelayControl import RelayControl
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
        self, vosekast, name, relay_port, valve_type, regulation,
    ):
        super().__init__()

        self.vosekast = vosekast
        self.name = name
        self._relay_port = relay_port
        self.valve_type = valve_type
        self.regulation = regulation
        self._state = self.UNKNOWN
        self.logger = logging.getLogger(LOGGER)
        self.state = self.UNKNOWN

    # todo fix bounce
    def close(self):
        """
        function to close the valve or switch
        :return:
        """
        self.logger.info("Closing {}".format(self.name))
        RelayControl.relays_off([self._relay_port])
        self.state = self.CLOSED

    def open(self):
        """
        open the valve
        :return:
        """
        self.logger.info("Opening {}".format(self.name))
        RelayControl.relays_on([self._relay_port])
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
