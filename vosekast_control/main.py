#!/usr/bin/python3

import sys
import os
import traceback
import asyncio

from vosekast_control.Log import setup_custom_logger

# add logger
logger = setup_custom_logger()


async def main(emulate=False):
    # overwrite the emulate param with the env if exist
    emulate = os.getenv("EMULATE", str(emulate)) == "True"

    # init vosekast variable
    vosekast = None

    # import the rpi module at event start to prevent the early opening of the emulator gui
    import RPi.GPIO as GPIO

    # import vosekast at runtime to prevent different event loops
    from vosekast_control.connectors import DBConnection
    from vosekast_control.Vosekast import Vosekast
    from vosekast_control.connectors import AppControl

    try:
        # initialise vosekast
        vosekast = Vosekast(GPIO, emulate=emulate)
        AppControl.start()

        # connect db
        DBConnection.connect()

        await vosekast.run()

    except Exception:
        logger.error(f"Problems with vosekast. Halt system.")
        traceback.print_exc()
        raise

    finally:
        AppControl.shutdown()
        if vosekast is not None:
            await vosekast.clean()
        DBConnection.close()
        GPIO.cleanup()

        if emulate:
            print("system exit")
            GPIO.ui.close()
            sys.exit(0)
        else:
            pass
            # os.system("sudo shutdown -h now")


if __name__ == "__main__":
    asyncio.run(main())
