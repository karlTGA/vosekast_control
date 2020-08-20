import logging
from vosekast_control.Log import LOGGER
from vosekast_control.utils.Msg import StatusMessage
from vosekast_control.connectors import MQTTConnection
from vosekast_control.connectors import RelayControl


class Pump:
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"
    UNKNOWN = "UNKNOWN"

    def __init__(self, vosekast, name, relay_port):
        super().__init__()

        self.vosekast = vosekast
        self.name = name
        self._relay_port = relay_port
        self.logger = logging.getLogger(LOGGER)
        self._state = self.UNKNOWN

    def stop(self):
        """
        stop the pump
        :return:
        """
        self.logger.info("Stopping {}".format(self.name))
        RelayControl.relays_off([self._relay_port])
        self.state = self.STOPPED

    def start(self):
        """
        start the pump
        :return:
        """
        self.logger.info("Starting {}".format(self.name))
        RelayControl.relays_on([self._relay_port])
        self.state = self.RUNNING

    def toggle(self):
        """
        toggle the pump
        """
        if self.state != self.RUNNING:
            self.start()
        else:
            self.stop()

    @property
    def is_stopped(self):
        return self.state == self.STOPPED

    @property
    def is_running(self):
        return self.state == self.RUNNING

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        self._state = new_state
        self.logger.info(f"New state of pump {self.name} is: {new_state}")
        self.publish_state()

    def publish_state(self):
        MQTTConnection.publish_message(StatusMessage("pump", self.name, self.state))
