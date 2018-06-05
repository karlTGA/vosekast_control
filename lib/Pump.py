class Pump:

    def __init__(self, name, control_pin, source_tank, target_tank, gpio_controller):
        self._pin = control_pin
        self.name = name
        self.source_tank = source_tank
        self.target_tank = target_tank
        self._gpio_controller = gpio_controller

        # init the gpio pin
        self._gpio_controller.setup(self._pin, self._gpio_controller.OUT)