import smbus
from typing import Dict, List


class RelayControl:
    def __init__(self, address=0x38):
        self.address = address
        self.bus = smbus.SMBus(1)
        self.state_reading = None
        self.state_binary = 255  # Represents relay address and inverted state in binary e.g. 0b11110101 -> relay 2 and 4 are "on"

    def relays_on(self, relay_list: List[int]):

        for relay in relay_list:
            self.state_binary = self.state_binary & ~(2 ** (relay - 1))

        self._flash()

    def relays_off(self, relay_list: List[int]):

        for relay in relay_list:
            self.state_binary = self.state_binary | 2 ** (relay - 1)

        self._flash()

    def get_state_dict(self) -> Dict[int, int]:
        state_dict = {}

        for i in range(8):
            state_dict[i] = (self.state_binary >> i) & 1

        return state_dict

    def read_state(self):
        # return state as read from the bus
        self.state_reading = self.bus.read_byte(self.address)
        return self.state_reading

    def all_off(self):
        self.state_binary = 255
        self._flash()

    def all_on(self):
        self.state_binary = 0
        self._flash()

    def _flash(self):
        self.bus.write_byte_data(self.address, 0, self.state_binary)


class I2CInput:
    def __init__(self, address=0x39):
        self.address = address
        self.bus = smbus.SMBus(1)

    def _read_state(self) -> int:
        state_reading = self.bus.read_byte(self.address)
        return state_reading

    def digitalRead(self, pin: int) -> int:
        bin_state = self._read_state()

        if pin >= 9 or pin <= 0:
            raise Exception("Pin is out of Range. Valid Pins are 1-8")

        pin_state = 1 ^ (1 & (bin_state >> (pin - 1)))
        return pin_state
