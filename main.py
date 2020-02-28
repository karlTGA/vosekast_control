#!/usr/bin/python3

import sys
import platform
import time
import subprocess
import os


#from lib.ExperimentEnvironment import ExperimentEnvironment

from lib.Log import setup_custom_logger
from lib.AppControl import AppControl
from multiprocessing.dummy import Pool as ThreadPool
import RPi.GPIO as GPIO
from lib.Vosekast import Vosekast

# add mqtt resources
import asyncio
import uvloop
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

# add logger
logger = setup_custom_logger()

#emulate default = False
EMULATE = os.environ.get('EMULATE', 'False')


async def main():
    try:
        #GPIO.cleanup()

        # process state
        app_control = AppControl()

        # initialise vosekast
        vosekast = Vosekast(app_control, GPIO, EMULATE == 'True')
        app_control.start()
        await vosekast.run()

        if EMULATE == 'True':
            sys.exit(0)
        else:
            #cmdCommand = "shutdown -h now"
            #subprocess.Popen(cmdCommand.split(), stdout=subprocess.PIPE)
            os.system('sudo shutdown -h now')
        
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
