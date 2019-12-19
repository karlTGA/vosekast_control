#!/usr/bin/python3

import sys
import platform
import time
import subprocess

from lib.ExperimentEnvironment import ExperimentEnvironment

from lib.Log import setup_custom_logger, add_status_box_handler
from lib.AppControl import AppControl
from multiprocessing.dummy import Pool as ThreadPool
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import QCoreApplication, QThreadPool
from lib.UI.MainWindow import MainWindow
import RPi.GPIO as GPIO

# add mqtt resources
import asyncio
import uvloop
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

# add logger
logger = setup_custom_logger()
DEBUG = True


async def main():
    # set mqtt host, token, message, topic
    host = 'localhost'
    token = None
    message = "vosekast start"
    topic = "system"

    # # mqtt client
    # controller = MQTTController(host)

    # await controller.connect()
    # await asyncio.sleep(0.1)

    # # mqtt server credentials
    # if token != None:
    #     controller.set_credentials(username, password)

    # # mqtt publish message
    # controller.publish(topic, message)
    # await asyncio.sleep(0.1)

    # process state
    app_control = AppControl()

    # add gui
    app = QApplication(sys.argv)
    main_window = MainWindow(app, app_control, GPIO, DEBUG)
    await main_window.run()

    # route log messages to status box of main window
    add_status_box_handler(main_window)
    app_control.start()

    # res = app.exec_()

    while True:
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
