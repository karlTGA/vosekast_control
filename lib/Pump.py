import logging
from lib.Log import LOGGER
from PyQt5.QtCore import pyqtSignal, QObject
from lib.EnumStates import States


class Pump(QObject):
    # signals
    state_changed = pyqtSignal(int, name="PumpStateChanged")

    def __init__(self, vosekast, name, control_pin, gpio_controller, gui_element):
        super().__init__()

        self.vosekast = vosekast
        self.name = name
        self._pin = control_pin
        self._gpio_controller = gpio_controller
        self.logger = logging.getLogger(LOGGER)
        self.state = States.NONE
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
        self.state = States.STOPPED
        self.state_changed.emit(States.STOPPED.value)
        self.vosekast.VosekastStore.dispatch({'type': 'Update ' + self.name, 'body': {'State': self.state.value}})


    def start(self):
        """
        start the pump
        :return:
        """
        self.logger.debug("Start the pump {}".format(self.name))
        self._gpio_controller.output(self._pin, self._gpio_controller.HIGH)
        self.state = States.RUNNING
        self.state_changed.emit(States.RUNNING.value)
        self.vosekast.VosekastStore.dispatch({'type': 'Update ' + self.name, 'body': {'State': self.state.value}})


    def toggle(self):
        """
        toggle the pump
        """
        if self.state != States.RUNNING:
            self.start()
        else:
            self.stop()
