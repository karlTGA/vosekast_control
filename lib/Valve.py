
class Valve:
    # regulations
    BINARY = 'BINARY'
    ANALOG = 'ANALOG'

    # valve_types
    TWO_WAY = 'TWO_WAY'
    THREE_WAY = 'THREE_WAY'
    SWITCH = 'SWITCH'

    def __init__(self, name, control_pin, valve_type, regulation, gpio_controller):
        self.name = name
        self._pin = control_pin
        self.valve_type = valve_type
        self.regulation = regulation
        self._gpio_controller = gpio_controller

        # init the gpio pin
        self._gpio_controller.setup(self._pin, self._gpio_controller.OUT)
