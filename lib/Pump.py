import logging
from lib.Log import LOGGER


class Pump:

    def __init__(self, name, control_pin, source_tank, target_tank, gpio_controller):
        self._pin = control_pin
        self.name = name
        self.source_tank = source_tank
        self.target_tank = target_tank
        self._gpio_controller = gpio_controller
        self.logger = logging.getLogger(LOGGER)

        # init the gpio pin
        self._gpio_controller.setup(self._pin, self._gpio_controller.OUT)

    def stop(self):
        """
        stop the pump
        :return:
        """
        self.logger.debug(F"Stop the pump F{self.name}")
        self._gpio_controller.output(self._pin, self._gpio_controller.LOW)
