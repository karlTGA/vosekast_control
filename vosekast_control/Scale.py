import serial
from collections import deque
from threading import Thread
from time import sleep
import time
from datetime import datetime
import logging
import traceback
from vosekast_control.Log import LOGGER
from random import uniform
from statistics import mean
from vosekast_control.utils.Msg import StatusMessage
from vosekast_control.connectors import MQTTConnection

from typing import Deque


class Scale:
    # Scale states
    UNKNOWN = "UNKNOWN"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    STOPPED = "STOPPED"

    def __init__(
        self,
        name,
        vosekast,
        port="/dev/serial0",
        baudrate=9600,
        bytesize=serial.SEVENBITS,
        timeout=1,
        emulate=False,
    ):
        super().__init__()

        self.name = name
        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.timeout = timeout
        self.connection = None
        self.last_values = deque([], 10)
        self.threads_started = False
        self.thread_readscale = Thread()
        self.emulate = emulate
        self.is_running = False
        self.stable = False
        self.logger = logging.getLogger(LOGGER)
        self.vosekast = vosekast
        self.state = self.UNKNOWN
        self.scale_publish = True
        self.threads = []
        self.scale_history = deque([], maxlen=200)
        self.flow_history = deque([], maxlen=100)
        self.scale_input_buffer: Deque[float] = deque([], 10)
        self.flow_history_average = deque([], maxlen=5)
        self.scale_start_value = 0

    def open_connection(self):
        if self.emulate:
            self.logger.info("Emulating open_connection scale.")

        else:
            ser = serial.Serial()
            ser.port = self.port
            ser.baudrate = self.baudrate
            ser.bytesize = self.bytesize
            ser.timeout = self.timeout

            self.connection = ser
            self.connection.open()
            self.logger.info("Opening connection to scale.")

    def close_connection(self):
        if self.emulate:
            self.logger.info("Emulating close_connection scale.")
        else:
            self.connection.close()
            self.logger.info("Closing connection to scale.")

    # def loop(self):
    #     self.logger.debug("Start measuring loop.")

        # check if already running
        # if not self.is_running:
        #     self.open_connection()
        #     self.start_measurement_thread()

        # while self.is_running:
            # new_value = self.handle_value_from_scale()

            # new_value_tare = new_value - self.scale_start_value

            # if new_value is not None:
            #     self.add_new_value(new_value_tare)
            # else:
            #     self.logger.warning("Reached loop with new value = None.")

            # sleep(1)

        # self.logger.info("Stopped measuring with scale.")

    def start(self):
        self.open_connection()
        self.start_measurement_thread()

    def start_measurement_thread(self):
        self.is_running = True

        if self.thread_readscale.is_alive():
            self.logger.info("Threads alive.")
            return
        else:
            self.thread_readscale = Thread(target=self._scale_input_buffer)
            self.threads.append(self.thread_readscale)
            self.logger.debug("Starting Thread readscale.")
            self.thread_readscale.start()
            self.threads_started = True

    # get initial value from scale
    def tare_start_value(self):

        if not self.emulate:
            self.scale_start_value = self.handle_value_from_scale()
        else:
            self.scale_start_value = 0

    def stop_measurement_thread(self):
        self.is_running = False

        # terminate threads
        if self.threads_started:
            self.thread_readscale.join()

        try:
            self.threads.remove(self.thread_readscale)
        except Exception:
            self.logger.error("Error while trying to stop measurement threads.")
            traceback.print_exc()
            # raise

        self.logger.debug("Stopped measurement thread.")
        self.threads_started = False

    # get value from scale (in own thread)
    def _scale_input_buffer(self):

        # clear scale_input
        scale_input = 0

        if not self.is_running:
            self.open_connection()
            self.start_measurement_thread()
            sleep(1)

        runs = 0
        self.scale_input_buffer.appendleft(0)

        while self.is_running:

            # get raw input from serial connection
            if not self.emulate and self.vosekast.state == self.vosekast.MEASURING:
                scale_input = self.connection.readline()
                self.scale_publish = True
            elif not self.emulate:
                scale_input = self.connection.readline()
                self.scale_publish = False
            # generate random values if self.emulate
            elif self.emulate and self.vosekast.state == self.vosekast.MEASURING:
                scale_input += uniform(0.022, 0.028)
                self.scale_publish = True
            elif self.emulate:
                scale_input = 0.0
                self.scale_publish = False

            # send only every "n"th value to add_new_value
            if runs == 20 and scale_input is not None:
                self.handle_value_from_scale(scale_input)
                runs = 0
            elif runs == 20 and scale_input is None:
                self.logger.warning("Reached loop with new value = None.")
                runs = 0

            self.scale_input_buffer.appendleft(scale_input)

            runs += 1
            sleep(0.05)

        self.logger.info("Scale stopped measuring.")

    # serial connection sometimes produces inconsistent readouts
    def handle_value_from_scale(self, scale_input):

        # handling of weird output from scale, needed if NOT self.emulate
        if not self.emulate:

            if len(scale_input) == 0:
                # write dummy value to deque
                scale_input = 0

                self.logger.warning(
                    "Cannot read from scale. Did you remember to turn on the scale?"
                )
                return
            elif len(scale_input) != 16:
                # write dummy value to deque
                scale_input = 0

                self.logger.info(
                    "readline() read less than 16 char."
                )
                return
            else:
                split_line = scale_input.split()

            if len(split_line) == 1:
                self.logger.warning("Scale output too short.")
                self.logger.debug("split_line: " + str(split_line))
                return
            else:
                split_line_formatted = split_line[1]
                split_line_str = split_line_formatted.decode("utf-8")
                new_value = float(split_line_str)

        elif self.emulate:
            new_value = scale_input

        self.tare(new_value)

    def tare(self, new_value):
        tared_value = new_value - self.scale_start_value
        self.add_new_value(tared_value)
        self.publish_values(tared_value)

    def add_new_value(self, tared_value):

        timestamp = time.time() * 1000

        # deque scale history
        self.scale_history.appendleft(timestamp)
        self.scale_history.appendleft(tared_value)

        # calculate volume flow
        if len(self.scale_history) > 2:

            try:
                # todo dictionary: value, timestamp
                delta = self.scale_history[0] - self.scale_history[2]
                delta_weight = abs(delta)

                duration = self.scale_history[1] - self.scale_history[3]
                delta_time = abs(duration)

                weight_per_time = (delta_weight / delta_time) * 1000

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
    def publish_values(self, tared_value):

        if not self.scale_publish:
            return
        else:
            MQTTConnection.publish_message(
                StatusMessage("scale", self.name, f"{tared_value} Kg")
            )

    def flow_average(self):
        volume_flow_average = mean(self.flow_history_average)
        flow_average = round(volume_flow_average, 5)
        return flow_average

    # get most current scale value
    # please note that this value has not been tared, or parsed by methods above
    def get_current_value(self):
        timestamp = datetime.now()
        current_value = self.scale_input_buffer[0]
        MQTTConnection.publish_message(StatusMessage("scale", self.name, f"{current_value} Kg at {timestamp}"))