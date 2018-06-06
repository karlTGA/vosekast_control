"""
Stand: 1.08
"""

import os
import time
import serial
from lib.Vosekast import Vosekast
from lib.Log import setup_custom_logger, LOGGER

# add logger
logger = setup_custom_logger(LOGGER)

# if on raspberry pi then with real GPIO. Alternative with emulator
(sysname, nodename, release, version, machine) = os.uname()
if machine.startswith('arm'):
    import RPi.GPIO as GPIO
else:
    from third_party.RPi_emu import GPIO


def main():
    try:
        # add vorsecast instance
        vk = Vosekast(GPIO)
        vk.prepare_measuring()

        while not vk.ready_to_measure():
            logger.info("Wait that vosekast is ready...")
            time.sleep(10)

        logger.info("Ready to rumble")
    except KeyboardInterrupt:
        logger.info("User stopped program")
    finally:
        if 'vk' in vars():
            vk.shutdown()
        GPIO.cleanup()

if __name__ == "__main__":
    main()

"""
Todo  
Thread zur Fehlerueberwachung: P2 darf nur laufen, wenn Schalter in Konnstantfass geschlossen, Timeout 
Start einfacher machen;  python ./python_vosekast2/main.py    
GUI
Einbindung Sensoren: Drossel, Temperatur, Pruefling
"""
