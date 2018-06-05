
class LevelSensor:
    # Positions
    HIGH = 'HIGH'
    LOW = 'LOW'

    def __init__(self, name, control_pin, sensor_type, position, gpio_controller):
        self.name = name
        self.sensor_type = sensor_type
        self.position = position
        self._pin = control_pin
        self._gpio_controller = gpio_controller

        # init gpio_pins
        self._gpio_controller.setup(self._pin, self._gpio_controller.OUT)
