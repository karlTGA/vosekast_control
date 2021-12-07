import serial
import itertools
from typing import List, Tuple, Union, Deque
from collections import deque
from threading import Thread, Event
import time
from asyncio import sleep
import logging
from datetime import datetime
from serial.serialutil import PARITY_EVEN
from vosekast_control.Log import LOGGER
from random import uniform
from vosekast_control.utils.Msg import StatusMessage
from vosekast_control.connectors import MQTTConnection
import io

logger = logging.getLogger(LOGGER)


class Reading:
    __slots__ = ("time", "value", "flow")

    def __init__(self, time: float, value: float, flow: float):
        self.time = time
        self.value = value
        self.flow = flow

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


class NoSerialConnectionError(Exception):
    pass


def parse_serial_output(line) -> Tuple[Union[float, None], bool]:
    splitted_line = line.split()
    stable = False
    unit = None

    if len(splitted_line) < 2 or len(splitted_line) > 3:
        logger.warning(
            f"Read line on scale with wrong format. [{line}] len({len(splitted_line)})"
        )
        return None, stable

    if splitted_line[0] == '0.000':
        number = 0.0
        if splitted_line[1] is not None:
            unit = splitted_line[1]

    elif len(splitted_line) == 2:
        # readed value is without unit -> not stable value
        # example: '+   0.015 \r\n'
        number = float(splitted_line[1])

    else:
        # readed value is with unit -> stable value
        # example: '+    0.009 kg \r\n'
        number = float(splitted_line[1])
        unit = splitted_line[2]
        stable = True

    # inverse value if measure negative value
    if splitted_line[0] == "-":
        number = number * -1

    if unit is not None and unit != "kg":
        raise WrongUnitOnScaleError

    return number, stable


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
        self._serial_port = None

        self._value_history: Deque[Reading] = deque([], maxlen=1000)
        self._flow_history: Deque[Reading] = deque([], maxlen=1000)
        self._measurement_thread = MeasurementThread(target=self._loop)
        self._is_stable = False

        self._state = self.INITED       

    def start(self):
        if self._serial_interface is None:
            self._create_serial_interface()

        self._open_serial_connection()
        self.lock_keys()
        self.tare()
        self.set_kilogramm_on_scale()
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

        cmd = b"\x1bT\r\n"
        logger.debug(f"Write to serial [{cmd}]")

        self._write_to_serial(cmd)
        logger.debug("Send tare command to scale.")

    def lock_keys(self):
        if not self.connected:
            logger.warning("Cannt lock keys of scale if not connected.")
            return

        self._write_to_serial(b"\x1bO\r\n")

    def unlock_keys(self):
        if not self.connected:
            logger.warning("Cannot unlock keys of scale if not connected.")

        self._write_to_serial(b"\x1bR\r\n")

    def set_kilogramm_on_scale(self):
        if not self.connected:
            logger.warning("Cannot set kilogramm on scale if not connected.")

        cmd = b"\033B\r\n"
        logger.debug(f"Write to serial [{cmd}]")
        self._write_to_serial(cmd)

    def get_values(self, number=5) -> List[Reading]:
        first_index = max(len(self._value_history) - number, 0)
        return list(itertools.islice(self._value_history, first_index, None))

    @property
    def last_reading(self) -> Union[Reading, None]:
        if len(self._value_history) >= 1:
            return self._value_history[-1]

        return None

    @property
    def state(self):
        return self._state

    @property
    def connected(self):
        if self._emulate:
            return True

        return self._serial_port.is_open

    def _write_to_serial(self, message: bytearray) -> int:
        if self._emulate:
            logger.debug(f"Send emulated message to serial device: {message}")
            return 1

        self._serial_interface.write(message.decode("utf-8"))
        return self._serial_interface.flush()

    def _create_serial_interface(self):
        if self._emulate:
            return

        ser = serial.Serial()
        ser.port = self._port
        ser.baudrate = self._baudrate
        ser.bytesize = self._bytesize
        ser.timeout = self._timeout
        ser.parity = PARITY_EVEN
        ser.timeout = 0.1

        self._serial_interface = io.TextIOWrapper(
            io.BufferedRWPair(ser, ser, 1), newline="\r\n", line_buffering=True
        )
        self._serial_port = ser

    def _open_serial_connection(self):
        if self._emulate:
            logger.debug("Emulating serial connection to scale.")
            return

        if self._serial_port.is_open:
            logger.info("Serial connection already open.")
            return

        self._serial_port.open()
        logger.debug("Opening serial connection to scale.")

    def _close_serial_connection(self):
        if self._emulate:
            logger.debug("Close emulated connection to serial device.")
            return

        self._serial_port.close()
        logger.debug("Closing connection to scale.")

    def _start_thread(self):
        if self._measurement_thread.is_alive():
            logger.debug("Scale already running. Skip starting of measurment thread.")
            return

        self._measurement_thread.start()

    async def _stop_thread(self):
        self._state = self.STOPPING
        self._measurement_thread.stop()

        while self._measurement_thread.is_alive():
            logger.debug("Wait that the measuremnt thread stops.")
            await sleep(1)

    def _loop(self):
        logger.debug("Start measuring loop.")

        while not self._measurement_thread.stopped():
            try:
                self._read_value()
                time.sleep(self.reading_interval)
            except ValueError or IndexError:
                logger.warning('Failed to parse signal from scale!')
            except NoConnectionError:
                logger.warning('Not connected to scale. Cant read value.')
            except NoSerialConnectionError:
                logger.warning('No serial connection to scale.')
            except WrongUnitOnScaleError:
                logger.error('Scale is configured with the wrong unit!')

        logger.info("Stopped measuring with scale.")

    def _read_value(self):
        now = datetime.utcnow().timestamp()

        if not self.connected:
            raise NoConnectionError

        if self._emulate:
            value = 0.0 + uniform(0.0, 0.2)
            self._stable = True
            self._value_history.append(Reading(time=now, value=value))
            MQTTConnection.publish_message(
                StatusMessage(
                    "scale",
                    "weight",
                    str(value),
                    {"scaleUnit": "kg", "scaleStable": True},
                )
            )
            return

        if self._serial_interface is None:
            raise NoSerialConnectionError
        
        lines = self._serial_interface.readlines(80)
        #readlines function argument -> Limitation to avoid errors when reading
        
        if len(lines) == 0:
            logger.debug("Read no lines from serial device.")
            return

        if lines[-1].find("C.E") > 0:
            logger.warning("Scale is in calibration mode. Wait...")
            return

        value, stable = parse_serial_output(lines[-1])

        if value is None:
            return
        volume_flow = self.calculate_volume_flow(now, value)
        self._value_history.append(Reading(time=now, value=value, flow=volume_flow))
        
        # publish this infos to the frontend
        MQTTConnection.publish_message(
            StatusMessage(
                "scale", "weight", str(value), {"scaleUnit": "kg", "scaleStable": stable}
            )
        )
        # publish this infos to the frontend
        MQTTConnection.publish_message(
            StatusMessage(
                "flow", "volume_flow", str(volume_flow), {"scaleUnit": "l/s", "scaleStable": stable}
            )
        )
    def calculate_volume_flow(self, time, value):
            
        #calculate volume flow:
        # density of water at normal pressure:
        # 10°C: 0.999702 kg/l
        # 15°C: 0.999103 kg/l    
        # 20°C: 0.998207 kg/l
        # 25°C: 0.997048 kg/l
        density = 0.999103
        

        if len(self._value_history) > 0:
            
            time_delta = time - self._value_history[-1].time
            weight_delta = value - self._value_history[-1].value
            volume_flow = abs(weight_delta) / (time_delta * density)
            
        else:
            logger.debug("Erster Wert")
            volume_flow = 0
        return volume_flow


    