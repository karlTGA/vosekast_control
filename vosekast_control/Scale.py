import serial
from collections import deque
from threading import Thread
from time import sleep
import logging
from Log import LOGGER
from random import uniform
from itertools import islice
from statistics import mean
from utils.Msg import StatusMessage

from EnumStates import States

from collections import deque
from datetime import datetime


class Scale:

    def __init__(
        self,
        vosekast,
        port="/dev/serial0",
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
        self.thread_loop = Thread()
        self.thread_readscale = Thread()
        self.emulate = emulate
        self.run = False
        self.timestamp = datetime.now()
        self.stable = False
        self.logger = logging.getLogger(LOGGER)
        self.vosekast = vosekast
        self.state = States.NONE
        self.mqtt = self.vosekast.mqtt_client
        self.threads = []
        self.scale_history = deque([], maxlen=200)
        self.flow_history = deque([], maxlen=100)
        self.scale_input_buffer = deque([], maxlen=10)
        self.flow_history_average = deque([], maxlen=5)

    def open_connection(self):
        if not self.emulate:
            ser = serial.Serial()
            ser.port = self.port
            ser.baudrate = self.baudrate
            ser.bytesize = self.bytesize
            ser.timeout = self.timeout

            self.connection = ser
            self.connection.open()
            self.logger.info("Opening connection to scale.")
        else:
            self.logger.info("Emulating open_connection scale.")

    def close_connection(self):
        if not self.emulate:
            self.connection.close()
            self.logger.info("Closing connection to scale.")
        else:
            self.logger.info("Emulating close_connection scale.")

    def loop(self):
        self.logger.debug("Start measuring loop.")

        # check if already running
        if self.is_running != True:
            self.open_connection()
            self.start_measurement_thread()

        while self.run:

            if self.emulate:
                new_value = 10.0 + uniform(0.0, 0.2)
                self.add_new_value(new_value)
                self.timestamp = datetime.now()
            else:
                new_value = self.read_value_from_scale()

                if new_value is not None:
                    self.add_new_value(new_value)
                    self.timestamp = datetime.now()
                    # deque scale history
                    self.scale_history.appendleft(self.timestamp)
                    self.scale_history.appendleft(new_value)
                else:
                    self.logger.warning("Reached loop with new value = None.")

            sleep(1)

        self.logger.info("Stopped measuring with scale.")

    @property
    def is_running(self):
        if self.run == True and self.thread_loop.is_alive == True:
            self.logger.debug("Scale ready.")
            return True
        elif self.run == True:
            self.logger.debug("Waiting for thread_loop.")
            return True
        elif self.run != True:
            self.logger.warning("self.run != True")
        else:
            self.logger.warning("Scale not ready. Printing diagnostics.")
            self.print_diagnostics()

    def start_measurement_thread(self):
        self.run = True

        if self.thread_loop.is_alive() and self.thread_readscale.is_alive():
            self.logger.info("Threads alive.")
            return
        else:
            self.thread_loop = Thread(target=self.loop)
            self.threads.append(self.thread_loop)
            self.thread_readscale = Thread(target=self._scale_input_buffer)
            self.threads.append(self.thread_readscale)
            self.logger.debug("Starting Threads loop & readscale.")
            self.thread_readscale.start()
            self.thread_loop.start()

    # diagnostics
    def print_diagnostics(self):
        self.logger.info("Printing diagnostics:")
        self.logger.info("self.threads: " + str(self.threads))
        self.logger.info("self.connection.is_open: " +
                          str(self.connection.is_open))
        self.logger.info("Thread loop alive: " +
                          str(self.thread_loop.is_alive()))
        self.logger.info("Thread readscale alive: " +
                          str(self.thread_readscale.is_alive()))
        self.logger.info("self.run = " + str(self.run))
        self.logger.info("constant_tank_ready: " +
                          str(self.vosekast.constant_tank.is_filled))
        self.logger.info("measuring_tank_ready: " + str(self.vosekast.measuring_drain_valve.is_closed
                                                         and not self.vosekast.measuring_tank.is_filled))
        self.logger.info("constant_pump_running: " +
                          str(self.vosekast.pump_constant_tank.is_running))
        self.logger.info("measuring_drain_valve.is_closed: " +
                         str(self.vosekast.measuring_drain_valve.is_closed))
        self.logger.info("measuring_tank.is_filled: " +
                         str(self.vosekast.measuring_tank.is_filled))


    def stop_measurement_thread(self):
        self.run = False

        # terminate threads
        self.thread_loop.join()
        self.thread_readscale.join()
        self.threads.remove(self.thread_loop)
        self.threads.remove(self.thread_readscale)
        self.logger.debug("Stopped measurement thread.")

    def _scale_input_buffer(self):
        if self.connection is not None and self.connection.is_open:
            self.scale_input_buffer.appendleft(b'+ 0.000 kg')
            while self.run:
                scale_input = self.connection.readline()

                # if readline reads less than 16 char reuse last value
                if len(scale_input) == 0:
                    scale_input = self.scale_input_buffer[0]
                    print(
                        "Cannot read from scale. Did you remember to turn on the scale?")
                    sleep(5)
                elif len(scale_input) != 16:
                    scale_input = self.scale_input_buffer[0]
                    print("readline() read less than 16 char. Reusing last value.")

                self.scale_input_buffer.appendleft(scale_input)
                sleep(0.05)

    def read_value_from_scale(self):
        if self.connection is not None and len(self.scale_history) > 0:
            line = self.scale_input_buffer[0]

            splitted_line = line.split()

            if len(splitted_line) == 3:
                splitted_line_formatted = splitted_line[1]

                # if splitted_line[0] == b'-':
                #     self.logger.warning("Negative weight. Discarding value.")
                #     return

                splitted_line_str = splitted_line_formatted.decode("utf-8")
                new_value = float(splitted_line_str)
                return new_value

            elif len(splitted_line) == 2:
                splitted_line_formatted = splitted_line[1]

                if splitted_line[0] == b'-':
                    self.logger.warning("Negative weight. Discarding value.")
                    print(splitted_line)
                    return
                if splitted_line[1] == b'kg':
                    self.logger.info("No input.")
                    print(splitted_line)
                    return

                splitted_line_str = splitted_line_formatted.decode("utf-8")
                new_value = float(splitted_line_str)
                return new_value
            else:
                self.logger.warning("Scale output too short.")

        elif self.connection is not None:
            return 0.00

        else:
            self.logger.debug(self.connection.is_open)
            self.logger.debug(self.connection)
            self.open_connection()
            self.logger.info("Initialising connection to scale. Please retry.")

    def add_new_value(self, new_value):

        # calculate volume flow
        if len(self.scale_history) > 2:
            
            try:
                # todo dictionary: value, timestamp
                delta = self.scale_history[0] - self.scale_history[2]
                delta_weight = abs(delta)

                duration = self.scale_history[1] - self.scale_history[3]
                abs_duration = abs(duration)
                delta_time = abs_duration.total_seconds()

                weight_per_time = delta_weight / delta_time

                # density of water at normal pressure:
                # 10°C: 0.999702
                # 15°C: 0.999103
                # 20°C: 0.998207

                # weight_per_time divided by density gives volume flow
                volume_flow = round(weight_per_time / 0.999103, 10)

                self.flow_history.appendleft(volume_flow)
                self.flow_history_average.appendleft(volume_flow)
            
            except ZeroDivisionError:
                self.logger.warning("Division by zero.")

        # publish via mqtt
        # new_value = weight measured by scale
        # volume_flow = calculated volume flow
        try:
            mqttmsg = StatusMessage(
                "scale", new_value, "Kg", volume_flow, "L/s")
        except:
            mqttmsg = StatusMessage("scale", new_value, "Kg", None, None)

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

    def flow_average(self):
        if len(self.flow_history_average) == 5:
            volume_flow_average = mean(self.flow_history_average)
            flow_average = round(volume_flow_average, 5)
            return flow_average
        else:
            return

    def get_stable_value(self):
        if self.stable:
            return self.last_values[-1]
        else:
            self.logger.warning("No stable value. Scale varies until now.")
            return 0
