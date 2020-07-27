import smbus
import time
bus = 
address_relays = 0x38
address_inputs = 0x39


class RelayControl():

    def __init__(self):
        self.address_relays = 0x38
        self.bus = smbus.SMBus(1)
        self.state_list = []
        self.read_state = None
        self.binary = 255  # Represents relay address and inverted state in binary e.g. 0b11110101 -> relay 2 and 4 are "on"

    def relays_on(self, relay_list):
        
        for relay in relay_list:
            self.binary = self.binary & ~ 2**(relay-1)


    def relays_off(self, relay_list):
        
        for relay in relay_list:
            self.binary = self.binary | 2**(relay-1)

    
    def get_state_list(self):
        n = 0
        self.state_list = []
        bin_string = "{0:b}".format(self.binary)
        for n in range(8) :
            self.state_list.append(bin_string[7-n])


    def read_state(self):
        # return state as read from the bus
        self.read_state = self.bus.read_byte_data(self.address_relays, 0)
        return self.read_state


    def all_off(self):
        self.binary = 255
        self.switch()

    def all_on(self):
        self.binary = 0
        self.switch()

    def switch():
        self.bus.write_byte_data(self.address_relays, 0, self.binary)