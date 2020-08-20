from typing import Optional, Any
import logging
from vosekast_control.Log import LOGGER

logger = logging.getLogger(LOGGER)


class SMBusConnector:
    smbus: Optional[Any]
    emulate: Optional[bool]

    def __init__(self):
        self.smbus = None
        self.emulate = None

    def init_bus(self, emulate=False):
        if self.smbus is not None:
            logger.warning("SMBus already inited. A second init is not possible.")

        self.emulate = emulate

        if self.emulate:
            from ..utils.SMBusMock import SMBus

            self.smbus = SMBus()
        else:
            import smbus

            self.smbus = smbus.SMBus(1)


SMBusConnection = SMBusConnector()
