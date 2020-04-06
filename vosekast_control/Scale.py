import serial
from collections import deque
from threading import Thread
from time import sleep
import time
import logging
from vosekast_control.Log import LOGGER
from random import uniform
from itertools import islice
from statistics import mean
from vosekast_control.utils.Msg import StatusMessage
from vosekast_control.connectors import DBConnection
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
        self.thread_loop = Thread()
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
        self.scale_input_buffer: Deque[float] = deque([], maxlen=10)
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
        if not self.is_running:
            self.open_connection()
            self.start_measurement_thread()

        while self.is_running:
            new_value = self.read_value_from_scale()

            if new_value is not None:
                self.add_new_value(new_value)
            else:
                self.logger.warning("Reached loop with new value = None.")

            sleep(1)

        self.logger.info("Stopped measuring with scale.")

    def start(self):
        self.open_connection()
        self.start_measurement_thread()

    def start_measurement_thread(self):
        self.is_running = True

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
            self.threads_started = True

    # diagnostics
    def print_diagnostics(self):
        self.logger.info(
            "Diagnostics:"
            + str(f"self.threads: {str(self.threads)}\n")
            + str(f"Thread loop alive: {str(self.thread_loop.is_alive())}\n")
            + str(f"Thread readscale alive: {str(self.thread_readscale.is_alive())}\n")
            + str(f"self.is_running: {str(self.is_running)}\n")
            + str(
                f"constant_tank_ready: {str(self.vosekast.constant_tank.is_filled)}\n"
            )
            + str(
                f"measuring_tank_ready: {str(self.vosekast.valves[MEASURING_DRAIN_VALVE].is_closed and not self.vosekast.tanks[MEASURING_TANK].is_filled)}\n"
            )
            + str(
                f"constant_pump_running: {str(self.vosekast.pumps[PUMP_CONSTANT_TANK].is_running)}\n"
            )
            + str(
                f"measuring_drain_valve.is_closed: {str(self.vosekast.valves[MEASURING_DRAIN_VALVE].is_closed)}\n"
            )
            + str(
                f"measuring_tank.is_filled: {str(self.vosekast.tanks[MEASURING_TANK].is_filled)}\n"
            )
            + str(f"constant_tank state: {str(self.vosekast.constant_tank.state)}\n")
            + str(
                f"measuring_tank state: {str(self.vosekast.tanks[MEASURING_TANK].state)}\n"
            )
            + str(f"db connection established: {str(DBConnection.isConnected)}")
        )
        if not self.emulate:
            self.logger.info("self.connection.is_open: " + str(self.connection.is_open))

    def stop_measurement_thread(self):
        self.is_running = False

        # terminate threads
        if self.threads_started:
            self.thread_loop.join()
            self.thread_readscale.join()
        try:
            self.threads.remove(self.thread_loop)
            self.threads.remove(self.thread_readscale)
        except Exception:
            pass
        self.logger.debug("Stopped measurement thread.")
        self.threads_started = False

    def _scale_input_buffer(self):
        if self.connection is not None and not self.emulate and self.connection.is_open:
            self.scale_input_buffer.appendleft(0)
            while self.is_running:
                scale_input = self.connection.readline()

                # if readline reads less than 16 char reuse last value
                if len(scale_input) == 0:
                    scale_input = self.scale_input_buffer[0]
                    self.logger.warning(
                        "Cannot read from scale. Did you remember to turn on the scale?"
                    )
                    sleep(5)
                    self.scale_publish = False
                elif len(scale_input) != 16:
                    scale_input = self.scale_input_buffer[0]
                    self.logger.info(
                        "readline() read less than 16 char. Reusing last value."
                    )
                    self.scale_publish = False
                else:
                    self.scale_publish = True

                self.scale_input_buffer.appendleft(scale_input)
                sleep(0.05)

        elif self.emulate:
            self.scale_input_buffer.appendleft(0)

            while self.is_running:

                if self.vosekast.state == self.vosekast.MEASURING:
                    scale_input += uniform(0.4, 0.5)
                    self.scale_publish = True
                else:
                    scale_input = 0.0 + uniform(0.0, 0.2)
                    self.scale_publish = False

                self.scale_input_buffer.appendleft(scale_input)
                sleep(1)

            scale_input = 0

    def read_value_from_scale(self):
        if self.connection is not None and len(self.scale_history) > 0:

            line = self.scale_input_buffer[0]

            split_line = line.split()

            if len(split_line) == 3:
                split_line_formatted = split_line[1]

                split_line_str = split_line_formatted.decode("utf-8")
                new_value = float(split_line_str)
                return new_value

            elif len(split_line) == 2:
                split_line_formatted = split_line[1]

                split_line_str = split_line_formatted.decode("utf-8")
                new_value = float(split_line_str)
                return new_value
            else:
                self.logger.warning("Scale output too short.")
                self.logger.debug("split_line: " + str(split_line))

        elif self.connection is not None:
            return 0.00

        elif self.emulate:
            split_line = self.scale_input_buffer[0]
            return split_line

        else:
            self.logger.debug(self.connection.is_open)
            self.logger.debug(self.connection)
            self.open_connection()
            self.logger.info("Initialising connection to scale. Please retry.")

    def add_new_value(self, new_value):

        timestamp = time.time() * 1000

        # deque scale history
        self.scale_history.appendleft(timestamp)
        self.scale_history.appendleft(new_value)

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
        # new_value = weight measured by scale

        if not self.scale_publish:
            return
        else:
            MQTTConnection.publish_message(
                StatusMessage("scale", self.name, f"{new_value} Kg")
            )

            if len(self.last_values) == 10:
                # calculate square mean error
                diffs = 0
                for value in list(islice(self.last_values, 0, 9)):
                    diffs += abs(value - new_value)

                mean_diff = diffs / len(self.last_values)

                if mean_diff < 0.1:
                    self.stable = True
                    self.state = self.RUNNING
                    return

            self.stable = False
            self.state = self.PAUSED

    def flow_average(self):
        if len(self.flow_history_average) == 5:
            volume_flow_average = mean(self.flow_history_average)
            flow_average = round(volume_flow_average, 5)
            return flow_average
        else:
            return 0

    def get_stable_value(self):
        if self.stable:
            return self.last_values[-1]
        else:
            self.logger.warning("No stable value. Scale varies until now.")
            return 0
