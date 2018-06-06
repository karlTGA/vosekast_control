
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
        self._gpio_controller.setup(self._pin, self._gpio_controller.IN)

        # add a thread for event detection
        if position == self.HIGH:
            self._gpio_controller.add_event_detect(self._pin, self._gpio_controller.RISING, bouncetime=200)
        else:
            self._gpio_controller.add_event_detect(self._pin, self._gpio_controller.FALLING, bouncetime=200)

    def add_callback(self, callback_function):
        """
        add a callback function, that fire every time the sensor is triggered
        :param callback_function: the function, that get fired
        :return:
        """
        self._gpio_controller.add_event_callback(self._pin, callback_function)

    def clear_callbacks(self):
        """
        remove all callbacks function and start with a clean state
        :return:
        """
        self._gpio_controller.remove_event_detect(self._pin)
        self._gpio_controller.add_event_detect(self._pin, self._gpio_controller.RISING, bouncetime=200)
