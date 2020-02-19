import RPi.GPIO as GPIO
from time import sleep


# GPIO Assignment
PIN_PUMP_CONSTANT = 17
PIN_PUMP_MEASURING = 27
PIN_VALVE_MEASURING_SWITCH = 12
PIN_VALVE_MEASURING_DRAIN = 18
PIN_LEVEL_MEASURING_HIGH = 24
PIN_LEVEL_MEASURING_LOW = 25
PIN_LEVEL_CONSTANT_LOW = 5
PIN_LEVEL_CONSTANT_HIGH = 6

class Testsensor():

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    

        try:
            self._gpio_controller = GPIO
            # define how the pins are numbered on the board
            self._gpio_controller.setmode(self._gpio_controller.BCM)
            self._gpio_controller.setup(6, GPIO.IN)

        except:
            pass

        
    def loop(self):
        while True:
            print(self._gpio_controller.input(6))
            sleep(1)

       