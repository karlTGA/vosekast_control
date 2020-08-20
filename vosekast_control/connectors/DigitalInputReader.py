from vosekast_control.connectors import SMBusConnection


class DigitalInputReaderConnector:
    def __init__(self, address=0x39):
        self.address = address

    def _read_state(self) -> int:
        state_reading = SMBusConnection.smbus.read_byte(self.address)
        return state_reading

    def digitalRead(self, pin: int) -> int:
        bin_state = self._read_state()

        if pin >= 9 or pin <= 0:
            raise Exception("Pin is out of Range. Valid Pins are 1-8")

        pin_state = 1 ^ (1 & (bin_state >> (pin - 1)))
        return pin_state


DigitalInputReader = DigitalInputReaderConnector()
