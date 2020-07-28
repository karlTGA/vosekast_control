import smbus


class RelayControl():

    def __init__(self):
        self.address_relays = 0x38
        self.bus = smbus.SMBus(1)
        self.state_dict = {}
        self.state_reading = None
        self.binary = 255  # Represents relay address and inverted state in binary e.g. 0b11110101 -> relay 2 and 4 are "on"


    def relays_on(self, relay_list):
        
        for relay in relay_list:
            self.binary = self.binary & ~ 2**(relay-1)
        
        self._flash()


    def relays_off(self, relay_list):

        for relay in relay_list:
            self.binary = self.binary | 2**(relay-1)

        self._flash()

    
    def get_state_dict(self):
        bin_state = format(self.binary, '07b')
        n = len(bin_state)
        for digit in bin_state:
            self.state_dict[n]= int(digit)
            n -= 1

        return self.state_dict


    def read_state(self):
        # return state as read from the bus
        self.state_reading = self.bus.read_byte(self.address_relays)
        return self.state_reading


    def all_off(self):
        self.binary = 255
        self._flash()


    def all_on(self):
        self.binary = 0
        self._flash()


    def _flash(self):
        self.bus.write_byte_data(self.address_relays, 0, self.binary)


class I2CInput():

    def __init__(self):
        self.address_input = 0x39
        self.bus = smbus.SMBus(1)
        self.state_reading = None

    def _read_state(self):
        self.state_reading = self.bus.read_byte(self.address_input)
        return self.state_reading

    def digitalRead(self, pin):
        bin_state = self._read_state()
        
        if pin >= 8 or pin <= 0:
            raise Exception("Pin is out of Range. Valid Pins are 1-7")

        pin_state = (1 & (bin_state >> (pin-1)))
        return pin_state