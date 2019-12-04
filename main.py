#!/usr/bin/python3

import sys
import platform
import time
import subprocess

from lib.Vosekast import Vosekast
from lib.ExperimentEnvironment import ExperimentEnvironment

from lib.Log import setup_custom_logger, add_status_box_handler
from lib.AppControl import AppControl
from multiprocessing.dummy import Pool as ThreadPool
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import QCoreApplication, QThreadPool
from lib.UI.MainWindow import MainWindow
import RPi.GPIO as GPIO

# add logger
logger = setup_custom_logger()
DEBUG = True

if __name__ == "__main__":
    # process state
    app_control = AppControl()

    # add gui
    app = QApplication(sys.argv)
    main_window = MainWindow(app, app_control, GPIO, DEBUG)

    # route log messages to status box of main window
    add_status_box_handler(main_window)

    app_control.start()

    res = app.exec_()
    logger.info("GUI closed. Shutdown Vosekast.")
    app_control.shutdown()

    if DEBUG:
        sys.exit(0)
    else:
        cmdCommand = "shutdown -h now"
        process = subprocess.Popen(cmdCommand.split(), stdout=subprocess.PIPE)
