#!/usr/bin/python3

import sys
import os
import traceback

from vosekast_control.Log import setup_custom_logger
from vosekast_control.AppControl import AppControl

# add mqtt resources
import asyncio

# add logger
logger = setup_custom_logger()


async def main(emulate=False):
    # overwrite the emulate param with the env if exist
    emulate = os.getenv("EMULATE", str(emulate)) == "True"

    # import the rpi module at event start to prevent the early opening of the emulator gui
    import RPi.GPIO as GPIO

    # import vosekast at runtime to prefend different event loops
    from vosekast_control.connectors import DBConnection
    from vosekast_control.Vosekast import Vosekast

    try:
        # GPIO.cleanup()

        # process state
        app_control = AppControl()

        # initialise vosekast
        vosekast = Vosekast(app_control, GPIO, emulate=emulate)
        app_control.start()

        # connect db
        DBConnection.connect()

        await vosekast.run()

    except Exception:
        traceback.print_exc(file=sys.stdout)

    finally:
        vosekast.clean()
        DBConnection.close()
        GPIO.cleanup()

        if emulate:
            print("system exit")
            sys.exit(0)
        else:
            os.system("sudo shutdown -h now")


if __name__ == "__main__":
    asyncio.run(main())
