import logging
from lib.Log import LOGGER


class Pump:
    # states
    RUNNING = 1
    STOPPED = 0

    def __init__(self, name, control_pin, gpio_controller):
        self._pin = control_pin
        self.name = name
        self._gpio_controller = gpio_controller
        self.logger = logging.getLogger(LOGGER)
        self.state = None

        # init the gpio pin
        self._gpio_controller.setup(self._pin, self._gpio_controller.OUT)

    def stop(self):
        """
        stop the pump
        :return:
        """
        self.logger.debug(F"Stop the pump {self.name}")
        self._gpio_controller.output(self._pin, self._gpio_controller.LOW)
        self.state = self.STOPPED

    def start(self):
        """
        start the pump
        :return:
        """
        self.logger.debug(F"Start the pump {self.name}")
        self._gpio_controller.output(self._pin, self._gpio_controller.HIGH)
        self.state = self.RUNNING