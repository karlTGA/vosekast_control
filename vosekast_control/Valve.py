import logging
from Log import LOGGER
from utils.Msg import StatusMessage


class Valve():
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
        self,
        vosekast,
        name,
        control_pin,
        valve_type,
        regulation,
        gpio_controller,
    ):
        super().__init__()

        self.vosekast = vosekast
        self.name = name
        self._pin = control_pin
        self.valve_type = valve_type
        self.regulation = regulation
        self._gpio_controller = gpio_controller
        self.logger = logging.getLogger(LOGGER)
        self.state = self.UNKNOWN
        self.mqtt = self.vosekast.mqtt_client

        # init the gpio pin
        self._gpio_controller.setup(self._pin, self._gpio_controller.OUT)

    #todo bounce 
    def close(self):
        """
        function to close the valve or switch
        :return:
        """
        self.logger.info("Closing {}".format(self.name))
        
        #todo this triggers bounce
        self._gpio_controller.output(self._pin, self._gpio_controller.LOW)
        
        self.state = self.CLOSED

        mqttmsg = StatusMessage(
                    self.name, "Closing {}".format(self.name), None, None, None)
        self.mqtt.publish_message(mqttmsg)

    def open(self):
        """
        open the valve
        :return:
        """
        self.logger.info("Opening {}".format(self.name))
        
        #todo this triggers bounce
        self._gpio_controller.output(self._pin, self._gpio_controller.HIGH)
        
        self.state = self.OPEN

        mqttmsg = StatusMessage(
                    self.name, "Opening {}".format(self.name), None, None, None)
        self.mqtt.publish_message(mqttmsg)

    @property
    def is_closed(self):
        return self.state == self.CLOSED

    @property
    def is_open(self):
        return self.state == self.OPEN   

