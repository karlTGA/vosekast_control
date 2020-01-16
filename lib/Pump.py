import logging
from lib.Log import LOGGER
from lib.EnumStates import States
from lib.utils.Msg import StatusMessage


class Pump():

    def __init__(self, vosekast, name, control_pin, gpio_controller):
        super().__init__()

        self.vosekast = vosekast
        self.name = name
        self._pin = control_pin
        self._gpio_controller = gpio_controller
        self.logger = logging.getLogger(LOGGER)
        self.state = States.NONE
        self.mqtt = self.vosekast.mqtt_client

        # init the gpio pin
        self._gpio_controller.setup(self._pin, self._gpio_controller.OUT)

    def stop(self):
        """
        stop the pump
        :return:
        """
        self.logger.debug("Stopping pump {}".format(self.name))
        self._gpio_controller.output(self._pin, self._gpio_controller.LOW)
        self.state = States.STOPPED

        # publish States.STOPPED.value via mqtt
        mqttmsg = StatusMessage(self.name, States.STOPPED.value, unit="%")
        if self.mqtt.connection_test():
            self.mqtt.publish_message(mqttmsg)

    def start(self):
        """
        start the pump
        :return:
        """
        self.logger.debug("Starting pump {}".format(self.name))
        self._gpio_controller.output(self._pin, self._gpio_controller.HIGH)
        self.state = States.RUNNING

        # publish States.RUNNING.value via mqtt
        mqttmsg = StatusMessage(self.name, States.RUNNING.value, unit="%")
        if self.mqtt.connection_test():
            self.mqtt.publish_message(mqttmsg)

    def toggle(self):
        """
        toggle the pump
        """
        if self.state != States.RUNNING:
            self.start()
        else:
            self.stop()
