class SMBus:
    _state: int

    def __init__(self):
        self._state = 255

    def read_byte(self, address) -> int:
        return self._state

    def write_byte_data(self, address: int, register: int, value: int):
        self._state = value
