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
import RPi.GPIO as GPIO
from vosekast_control.Vosekast import Vosekast

# add mqtt resources
import asyncio

# add logger
logger = setup_custom_logger()


async def main(emulate=False):
    try:
        #GPIO.cleanup()

        # process state
        app_control = AppControl()

        # initialise vosekast
        vosekast = Vosekast(app_control, GPIO, emulate=emulate)
        app_control.start()
        await vosekast.run()

        if emulate:
            sys.exit(0)
        else:
            os.system('sudo shutdown -h now')
    finally:
        vosekast.clean()
        GPIO.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
