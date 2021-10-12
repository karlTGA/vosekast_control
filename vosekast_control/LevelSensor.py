from vosekast_control.connectors import MQTTConnection
from vosekast_control.utils.Msg import StatusMessage
from vosekast_control.connectors.DigitalInputReader import DigitalInputReader


class LevelSensor:
    # Positions
    HIGH = "HIGH"
    LOW = "LOW"

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
