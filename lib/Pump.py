import logging
from lib.Log import LOGGER
from PyQt5.QtCore import pyqtSignal, QObject


class Pump(QObject):
    # states
    RUNNING = 1
    STOPPED = 0

    # signals
    state_changed = pyqtSignal(int, name="PumpStateChanged")

    def __init__(self, name, control_pin, gpio_controller, gui_element):
        super().__init__()

        self._pin = control_pin
        self.name = name
        self._gpio_controller = gpio_controller
        self.logger = logging.getLogger(LOGGER)
        self.state = None
        self.gui_element = gui_element

        # init the gpio pin
        self._gpio_controller.setup(self._pin, self._gpio_controller.OUT)

        # signals for gui
        self.state_changed.connect(self.gui_element.state_change)

        # add to the button instance the pump instance
        self.gui_element.set_pump(self)

    def stop(self):
        """
        stop the pump
        :return:
        """
        self.logger.debug("Stop the pump {}".format(self.name))
        self._gpio_controller.output(self._pin, self._gpio_controller.LOW)
        self.state = self.STOPPED
        self.state_changed.emit(self.STOPPED)

    def start(self):
        """
        start the pump
        :return:
        """
        self.logger.debug("Start the pump {}".format(self.name))
        self._gpio_controller.output(self._pin, self._gpio_controller.HIGH)
        self.state = self.RUNNING
        self.state_changed.emit(self.RUNNING)
