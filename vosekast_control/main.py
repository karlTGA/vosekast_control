#!/usr/bin/python3

import sys
import platform
import time
import subprocess
import os
import traceback

from vosekast_control.Log import setup_custom_logger
from vosekast_control.AppControl import AppControl
from multiprocessing.dummy import Pool as ThreadPool
from vosekast_control.Vosekast import Vosekast
from vosekast_control.DB import db_instance

# add mqtt resources
import asyncio

# add logger
logger = setup_custom_logger()


async def main(emulate=False):
    # import the rpi module at event start to prevent the early opening of the emulator gui
    import RPi.GPIO as GPIO

    try:
        # GPIO.cleanup()

        # process state
        app_control = AppControl()

        # initialise vosekast
        vosekast = Vosekast(app_control, GPIO, emulate=emulate)
        app_control.start()

        await vosekast.run()
    
    finally:
        vosekast.clean()
        db_instance.close()
        GPIO.cleanup()
        
        if emulate:
            sys.exit(0)
            print("system exit")
        else:
            os.system('sudo shutdown -h now')

if __name__ == "__main__":
    asyncio.run(main())
