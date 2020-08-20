from typing import Dict, List
from vosekast_control.connectors import SMBusConnection
import logging
from vosekast_control.Log import LOGGER

logger = logging.getLogger(LOGGER)


class RelayControlConnector:
    def __init__(self, address=0x38):
        self.address = address

        self.state_binary = 255  # Represents relay address and inverted state in binary e.g. 0b11110101 -> relay 2 and 4 are "on"

    def relays_on(self, relay_list: List[int]):

        for relay in relay_list:
            if relay < 1:
                raise WrongRelayPort(
                    "The request relay port to toggle is 0 or lower. That is not possible."
                )

            self.state_binary = self.state_binary & ~(2 ** (relay - 1))

        self._flash()

    def relays_off(self, relay_list: List[int]):
        for relay in relay_list:
            if relay < 1:
                raise WrongRelayPort(
                    "The request relay port to toggle is 0 or lower. That is not possible."
                )

            self.state_binary = self.state_binary | 2 ** (relay - 1)

        self._flash()

    def get_state_dict(self) -> Dict[int, bool]:
        state_dict = {}

        for i in range(1, 9):
            state_dict[i] = (self.state_binary >> (i - 1)) & 1 != 1

        return state_dict

    def read_state(self) -> int:
        # return state as read from the bus
        return SMBusConnection.smbus.read_byte(self.address)

    def all_off(self):
        self.state_binary = 255
        self._flash()

    def all_on(self):
        self.state_binary = 0
        self._flash()

    def _flash(self):
        SMBusConnection.smbus.write_byte_data(self.address, 1, self.state_binary)


RelayControl = RelayControlConnector()


class WrongRelayPort(Exception):
    pass
