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

    # import vosekast at runtime to prevent different event loops
    from vosekast_control.connectors import DBConnection
    from vosekast_control.Vosekast import Vosekast
    from vosekast_control.connectors import AppControl
    from vosekast_control.connectors import SMBusConnection

    try:
        # init smbus
        SMBusConnection.init_bus(emulate=emulate)

        # initialise vosekast
        vosekast = Vosekast(emulate=emulate)
        AppControl.start()

        # connect db
        DBConnection.connect()

        await vosekast.run()

    except Exception:
        logger.error(f"Problems with vosekast. Halt system.")
        traceback.print_exc()
        raise

    finally:
        if vosekast is not None:
            await vosekast.shutdown()
        DBConnection.close()

        if emulate:
            print("system exit")
        else:
            pass
            # os.system("sudo shutdown -h now")


if __name__ == "__main__":
    asyncio.run(main())
