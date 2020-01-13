import logging
from lib.Log import LOGGER
from lib.EnumStates import States
from lib.utils.Msg import StatusMessage, ErrorMessage


class Valve():
    # regulations
    BINARY = "BINARY"
    ANALOG = "ANALOG"

    # valve_types
    TWO_WAY = "TWO_WAY"
    THREE_WAY = "THREE_WAY"
    SWITCH = "SWITCH"

    def __init__(
        self,
        vosekast,
        name,
        control_pin,
        valve_type,
        regulation,
        gpio_controller,
        button,
    ):
        super().__init__()

        self.vosekast = vosekast
        self.name = name
        self._pin = control_pin
        self.valve_type = valve_type
        self.regulation = regulation
        self._gpio_controller = gpio_controller
        self.logger = logging.getLogger(LOGGER)
        self.state = None
        self.mqtt = self.vosekast.mqtt_client

        # init the gpio pin
        self._gpio_controller.setup(self._pin, self._gpio_controller.OUT)

    def close(self):
        """
        function to close the valve or switch
        :return:
        """
        self.logger.debug("Close valve {}".format(self.name))
        self._gpio_controller.output(self._pin, self._gpio_controller.LOW)
        self.state = States.CLOSED
        # self.state_changed.emit(States.CLOSED.value)

        # publish States.CLOSED.value via mqtt
        mqttmsg = StatusMessage(self.name, "Closing valve {}", unit=None)
        if self.mqtt.connection_test():
            self.mqtt.publish_message(mqttmsg)

    def open(self):
        """
        open the valve
        :return:
        """
        self.logger.debug("Open valve {}".format(self.name))
        self._gpio_controller.output(self._pin, self._gpio_controller.HIGH)
        self.state = States.OPEN
        # self.state_changed.emit(States.OPEN.value)

        # publish States.OPEN.value via mqtt
        mqttmsg = StatusMessage(self.name, "Opening valve {}", unit=None)
        if self.mqtt.connection_test():
            self.mqtt.publish_message(mqttmsg)
