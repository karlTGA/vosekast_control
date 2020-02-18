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

    # process state
    app_control = AppControl()

    # initialise vosekast
    vosekast = Vosekast(GPIO, EMULATE == 'True')
    await vosekast.run()

    # route log messages to status box of main window
    #app_control.start()
    print("main")

    # res = app.exec_()

    while True:
        print("main loop")
        await asyncio.sleep(1)

    logger.info('start thread')

    logger.info("GUI closed. Shutdown Vosekast.")
    app_control.shutdown()

    if DEBUG:
        sys.exit(0)
    else:
        cmdCommand = "shutdown -h now"
        process = subprocess.Popen(cmdCommand.split(), stdout=subprocess.PIPE)

if __name__ == "__main__":
    asyncio.run(main())
