import serial
from collections import deque
from threading import Thread
from time import sleep
import logging
from lib.Log import LOGGER
from random import uniform
from itertools import islice
from lib.utils.Msg import StatusMessage

from lib.EnumStates import States


class Scale:

    def __init__(
        self,
        vosekast,
        port="/dev/ttyS0",
        baudrate=9600,
        bytesize=serial.SEVENBITS,
        timeout=1,
        emulate=False,
    ):
        super().__init__()

        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.timeout = timeout
        self.connection = None
        self.last_values = deque([], 10)
        self.thread = Thread(target=self.loop)
        self.emulate = emulate
        self.run = False
        self.stable = False
        self.logger = logging.getLogger(LOGGER)
        self.vosekast = vosekast
        self.state = States.NONE
        self.mqtt = self.vosekast.mqtt_client

        self.start_measurement_thread()

    def open_connection(self):
        if not self.emulate:
            ser = serial.Serial()
            ser.port = self.port
            ser.baudrate = self.baudrate
            ser.bytesize = self.bytesize
            ser.timeout = self.timeout

            self.connection = ser
            self.connection.open()

    def close_connection(self):
        if not self.emulate:
            self.connection.close()

    def loop(self):
        self.logger.info("Start measuring with scale.")
        while self.run:
            if self.emulate:
                self.add_new_value(10.0 + uniform(0.0, 0.2))
            else:
                new_value = self.read_value_from_scale()
                if new_value is not None:
                    self.add_new_value(new_value)
            sleep(5)

        self.logger.info("Stopped measuring with scale.")

    def start_measurement_thread(self):
        self.run = True
        self.thread.start()

    def stop_measurement_thread(self):
        self.run = False

    def read_value_from_scale(self):
        if self.connection.is_open:
            line = self.connection.readline()
            splitted_line = line.split()

            self.logger.info("Measured {}".format(line))

            if len(splitted_line) == 3:
                new_value = "".join(splitted_line[:2])
                return new_value

    def add_new_value(self, new_value):
        self.last_values.append(new_value)

        # publish new_value via mqtt
        mqttmsg = StatusMessage("scale", new_value, unit="Kg")
        if self.mqtt.connection_test():
            self.mqtt.publish_message(mqttmsg)

        if len(self.last_values) == 10:
            # calculate square mean error
            diffs = 0
            for value in list(islice(self.last_values, 0, 9)):
                diffs += abs(value - new_value)

            mean_diff = diffs / len(self.last_values)

            if mean_diff < 0.1:
                self.stable = True
                self.state = States.RUNNING
                return

        self.stable = False
        self.state = States.PAUSE

    def get_stable_value(self):
        if self.stable:
            return self.last_values[-1]
        else:
            self.logger.warning("No stable value. Scale varies until now.")
            return 0
