import serial
from typing import Tuple
from collections import deque
from threading import Thread, Event
import time
from asyncio import sleep
import logging
from datetime import datetime
from vosekast_control.Log import LOGGER
from random import uniform
from vosekast_control.utils.Msg import StatusMessage
from vosekast_control.connectors import MQTTConnection
import io

from typing import Deque

logger = logging.getLogger(LOGGER)


class Reading:
    __slots__ = ("time", "value")

    def __init__(self, time: float, value: float):
        self.time = time
        self.value = value


class MeasurementThread(Thread):
    def __init__(self, *args, **kwargs):
        super(MeasurementThread, self).__init__(*args, **kwargs)
        self._stop_event = Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


class NoConnectionError(Exception):
    pass


class WrongUnitOnScaleError(Exception):
    pass


def parse_serial_output(line) -> Tuple[float, bool]:
    splitted_line = line.split()

    if 1 < len(splitted_line) < 4:
        logger.warning("Read line on scale with wrong format.")
        return

    sign = splitted_line[0]
    number = float(splitted_line[1])
    if sign == "-":
        number = number * -1

    if len(splitted_line) == 3:
        if splitted_line[2] != "g":
            raise WrongUnitOnScaleError()

        return (number, True)

    return (number, False)


class Scale:
    # Scale states
    INITED = "INITED"
    RUNNING = "RUNNING"
    STOPPING = "STOPPING"
    STOPPED = "STOPPED"

    def __init__(
        self,
        name,
        port="/dev/serial0",
        baudrate=9600,
        bytesize=serial.SEVENBITS,
        timeout=1,
        emulate=False,
        reading_interval=1,
    ):
        super().__init__()

        self.name = name
        self.reading_interval = reading_interval
        self._emulate = emulate

        self._port = port
        self._baudrate = baudrate
        self._bytesize = bytesize
        self._timeout = timeout
        self._serial_interface = None

        self._value_history: Deque[Reading] = deque([], maxlen=1000)
        self._measurement_thread = MeasurementThread(target=self._loop)
        self._is_stable = False

        self._state = self.INITED

    def start(self):
        if self._serial_interface is None:
            self._create_serial_interface()

        self._open_serial_connection()
        self.lock_keys()
        self.tare()
        self.set_gramm_on_scale()
        self._start_thread()
        self._state = self.RUNNING

    async def stop(self):
        self.unlock_keys()
        self._close_serial_connection()
        await self._stop_thread()
        self._state = self.STOPPED

    def tare(self):
        if not self.connected:
            logger.warning("Cannt tare scale if not connected.")
            return

        self._write_to_serial("\x1bT\r\n")
        logger.debug("Send tare command to scale.")

    def lock_keys(self):
        if not self.connected:
            logger.warning("Cannt lock keys of scale if not connected.")
            return

        self._write_to_serial("\x1bO\r\n")

    def unlock_keys(self):
        if not self.connected:
            logger.warning("Cannot unlock keys of scale if not connected.")

        self._write_to_serial("\x1bR\r\n")

    def set_gramm_on_scale(self):
        if not self.connected:
            logger.warning("Cannot set gramm on scale if not connected.")

        self._write_to_serial("\x1bA\r\n")

    @property
    def value(self) -> Reading:
        return self._value_history[-1]

    @property
    def state(self):
        return self._state

    @property
    def connected(self):
        if self._emulate:
            return True

        return self._serial_interface.is_open

    def _write_to_serial(self, message: str) -> int:
        if self._emulate:
            logger.debug(f"Send emulated message to serial device: {message}")
            return

        return self._serial_interface.write(message)

    def _create_serial_interface(self):
        if self._emulate:
            return

        ser = serial.Serial()
        ser.port = self._port
        ser.baudrate = self._baudrate
        ser.bytesize = self._bytesize
        ser.timeout = self._timeout

        self._serial_interface = io.TextIOWrapper(
            io.BufferedRWPair(ser, ser, 1), newline="\r\n", line_buffering=True
        )

    def _open_serial_connection(self):
        if self._emulate:
            logger.debug("Emulating serial connection to scale.")
            return

        if self._serial_interface.is_open:
            logger.info("Serial connection already open.")
            return

        self._serial_interface.open()
        logger.debug("Opening serial connection to scale.")

    def _close_serial_connection(self):
        if self._emulate:
            logger.debug("Close emulated connection to serial device.")
            return

        self._serial_interface.close()
        logger.debug("Closing connection to scale.")

    def _start_thread(self):
        self._measurement_thread.start()

    async def _stop_thread(self):
        self._state = self.STOPPING
        self._measurement_thread.stop()

        while self._measurement_thread.is_alive():
            logger.debug("Wait that the measuremnt thread stops.")
            sleep(1)

    def _loop(self):
        logger.debug("Start measuring loop.")

        while not self._measurement_thread.stopped:
            self._read_value()
            time.sleep(self.reading_interval)

        logger.info("Stopped measuring with scale.")

    def _read_value(self):
        now = datetime.utcnow().timestamp()

        if not self.connected:
            raise NoConnectionError

        if self._emulate:
            self._stable = True
            self._value_history.append(Reading(time=now, value=0.0 + uniform(0.0, 0.2)))
            return

        lines = self._serial_interface.readlines()

        if len(lines) == 0:
            logger.debug("Read no lines from serial device.")
            return

        (value, is_stable) = parse_serial_output(lines[-1])

        self._value_history.append(
            Reading(time=now, value=parse_serial_output(lines[-1]))
        )
        self._is_stable = is_stable

        # publish this infos to the frontend
        MQTTConnection.publish_message(
            StatusMessage("scale", "stability", str(self._is_stable))
        )
        MQTTConnection.publish_message(StatusMessage("scale", "weight", f"{value} g"))

    # def add_new_value(self, new_value):

    #     timestamp = time.time() * 1000

    #     # deque scale history
    #     self.scale_history.appendleft(timestamp)
    #     self.scale_history.appendleft(new_value)

    #     # calculate volume flow
    #     if len(self.scale_history) > 2:

    #         try:
    #             # todo dictionary: value, timestamp
    #             delta = self.scale_history[0] - self.scale_history[2]
    #             delta_weight = abs(delta)

    #             duration = self.scale_history[1] - self.scale_history[3]
    #             delta_time = abs(duration)

    #             weight_per_time = (delta_weight / delta_time) * 1000

    #             # density of water at normal pressure:
    #             # 10°C: 0.999702
    #             # 15°C: 0.999103
    #             # 20°C: 0.998207

    #             # weight_per_time divided by density gives volume flow
    #             volume_flow = round(weight_per_time / 0.999103, 10)

    #             self.flow_history.appendleft(volume_flow)
    #             self.flow_history_average.appendleft(volume_flow)

    #         except ZeroDivisionError:
    #             logger.warning("Division by zero.")

    #     # publish via mqtt
    #     # new_value = weight measured by scale

    #     if not self.scale_publish:
    #         return
    #     else:
    #         MQTTConnection.publish_message(
    #             StatusMessage("scale", self.name, f"{new_value} Kg")
    #         )

    #         if len(self.last_values) == 10:
    #             # calculate square mean error
    #             diffs = 0
    #             for value in list(islice(self.last_values, 0, 9)):
    #                 diffs += abs(value - new_value)

    #             mean_diff = diffs / len(self.last_values)

    #             if mean_diff < 0.1:
    #                 self.stable = True
    #                 self.state = self.RUNNING
    #                 return

    #         self.stable = False
    #         self.state = self.PAUSED

    # def flow_average(self):
    #     if len(self.flow_history_average) == 5:
    #         volume_flow_average = mean(self.flow_history_average)
    #         flow_average = round(volume_flow_average, 5)
    #         return flow_average
    #     else:
    #         return 0
