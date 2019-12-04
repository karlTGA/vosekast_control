import logging
from lib.Log import LOGGER
from PyQt5.QtCore import pyqtSignal, QObject
from lib.EnumStates import States


class Valve(QObject):
    # regulations
    BINARY = "BINARY"
    ANALOG = "ANALOG"

    # valve_types
    TWO_WAY = "TWO_WAY"
    THREE_WAY = "THREE_WAY"
    SWITCH = "SWITCH"

    # signals
    state_changed = pyqtSignal(int, name="PumpStateChanged")

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
        self.gui_button = button
        self.state = None

        # init the gpio pin
        self._gpio_controller.setup(self._pin, self._gpio_controller.OUT)

        # add to the button instance the valve instance
        self.gui_button.set_valve(self)

        # signals for gui
        self.state_changed.connect(self.gui_button.state_change)

    def close(self):
        """
        function close the valve or switch
        :return:
        """
        self.logger.debug("Close valve {}".format(self.name))
        self._gpio_controller.output(self._pin, self._gpio_controller.LOW)
        self.state = States.CLOSED
        self.state_changed.emit(States.CLOSED.value)
        self.vosekast.VosekastStore.dispatch(
            {"type": "Update " + self.name, "body": {"State": self.state.value}}
        )

    def open(self):
        """
        open the valve
        :return:
        """
        self.logger.debug("Open valve {}".format(self.name))
        self._gpio_controller.output(self._pin, self._gpio_controller.HIGH)
        self.state = States.OPEN
        self.state_changed.emit(States.OPEN.value)
        self.vosekast.VosekastStore.dispatch(
            {"type": "Update " + self.name, "body": {"State": self.state.value}}
        )
