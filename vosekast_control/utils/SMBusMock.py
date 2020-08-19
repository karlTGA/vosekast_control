class SMBus:
    def __init__(self, size=4):
        self._state = bytearray(size)

    def read_byte(self, address) -> int:
        return self._state[0]

    def write_byte_data(self, address: int, register: int, value: int):
        if register >= len(self._state):
            raise IndexError(
                "Try to modify register in dummy smbus device, that not exist."
            )

        self._state[register] = value
