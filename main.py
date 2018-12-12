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
from lib.UI.MainWindow import MainWindow



# if on raspberry pi then with real GPIO. Alternative with emulator
(sysname, nodename, release, version, machine, processor) = platform.uname()
if machine.startswith('arm'):
    import RPi.GPIO as GPIO
    DEBUG = False
else:
    from third_party.RPi_emu import GPIO
    DEBUG = True

# add logger
logger = setup_custom_logger()


def core_vorsekast(app_control, gui_main_window):
    try:
        # add vorsecast instance
        logger.debug('Here')
        vk = Vosekast(GPIO, gui_main_window, DEBUG)
        logger.debug('Here')

        expEnv = ExperimentEnvironment(5,
            vosekast=vk,
            main_window=gui_main_window,
        )
        logger.debug('Here')

        vk.prepare_measuring()

        while not vk.ready_to_measure():
            if app_control.is_terminating():
                break
            logger.info("Wait that vosekast is ready...")
            time.sleep(1)
        else:
            logger.info("Ready to rumble")

    except KeyboardInterrupt:
        logger.info("User stopped program")
    except Exception as error:
        logger.error(error)

    finally:
        if 'vk' in vars():
            vk.shutdown()
        GPIO.cleanup()

if __name__ == "__main__":
    # process state
    app_control = AppControl()

    # add gui
    app = QApplication(sys.argv)
    main_window = MainWindow(app, app_control, DEBUG)

    # route log messages to status box of main window
    add_status_box_handler(main_window)

    # start separate thread with core methods
    pool = ThreadPool()
    pool.apply_async(core_vorsekast, [app_control, main_window])

    app_control.start()
    res = app.exec_()
    logger.info("GUI closed. Shutdown Vosekast.")
    app_control.shutdown()




    if DEBUG:
        sys.exit(0)
    else:
        cmdCommand = "shutdown -h now"
        process = subprocess.Popen(cmdCommand.split(), stdout=subprocess.PIPE)
