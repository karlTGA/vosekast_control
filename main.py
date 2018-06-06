#!/usr/bin/python3

import sys
import os
import time
from lib.Vosekast import Vosekast
from lib.Log import setup_custom_logger, LOGGER
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool
from PyQt5.QtWidgets import QApplication, QWidget
from lib.UI.MainWindow import MainWindow

# if on raspberry pi then with real GPIO. Alternative with emulator
(sysname, nodename, release, version, machine) = os.uname()
if machine.startswith('arm'):
    import RPi.GPIO as GPIO
else:
    from third_party.RPi_emu import GPIO

# add logger
logger = setup_custom_logger(LOGGER)


def core_vorsekast():
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


def gui_vorsekast():
    app = QApplication(sys.argv)
    main_window = MainWindow()

    sys.exit(app.exec_())

if __name__ == "__main__":
    pool = ThreadPool()
    pool.apply(gui_vorsekast)
    pool.apply(core_vorsekast)
