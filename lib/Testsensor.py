import RPi.GPIO as GPIO
from time import sleep
from datetime import datetime



# GPIO Assignment
PIN_PUMP_CONSTANT = 17
PIN_PUMP_MEASURING = 27
PIN_VALVE_MEASURING_SWITCH = 12
PIN_VALVE_MEASURING_DRAIN = 18
PIN_LEVEL_MEASURING_HIGH = 24
PIN_LEVEL_MEASURING_LOW = 25
PIN_LEVEL_CONSTANT_LOW = 5
PIN_LEVEL_CONSTANT_HIGH = 6

GPIO.setmode(GPIO.BCM)

GPIO.setup(5, GPIO.IN)
GPIO.setup(6, GPIO.IN)

print("printing GPIO.input:")        

while True:
    constant_high_old = GPIO.input(6)
    sleep(0.1)
    constant_high_new = GPIO.input(6)

    if constant_high_old == constant_high_new:
        pass
    else:
        print("LEVEL_CONSTANT_HIGH = " + str(GPIO.input(6)) + " " + str(datetime.now()))
        #print("LEVEL_CONSTANT_LOW = " + str(GPIO.input(5)))
    

       