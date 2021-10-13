from typing import Callable
from vosekast_control.connectors import MQTTConnection
from vosekast_control.utils.Msg import StatusMessage
from vosekast_control.connectors.DigitalInputReader import DigitalInputReader
import logging

from vosekast_control.Log import LOGGER

logger = logging.getLogger(LOGGER)


class LevelSensor:
    # Positions
    HIGH = "HIGH"
    LOW = "LOW"
    name: str
    sensor_type: str
    position: str
    _input_pin: int

    def __init__(self, name, input_pin, sensor_type, position):
        self.name = name
        self.sensor_type = sensor_type
        self.position = position
        self._input_pin = input_pin

    @property
    def state(self):
        return DigitalInputReader.digital_read(self._input_pin)

    def publish_state(self):
        new_state = "triggered" if self.state else "untriggered"
        MQTTConnection.publish_message(
            StatusMessage("level_sensor", self.name, new_state)
        )

    def add_callback(self, callback: Callable[[bool], None]):
        if self._input_pin in DigitalInputReader.callbacks:
            logger.warning("It is not possible to add two callbacks for a levelsensor.")

        DigitalInputReader.add_callback(self._input_pin, callback)

    def clear_callback(self):
        DigitalInputReader.clear_callback(self._input_pin)
        self._callback_id = None
