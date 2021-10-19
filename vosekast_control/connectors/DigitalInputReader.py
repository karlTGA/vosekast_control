from typing import Callable, Dict, List, Optional
from vosekast_control.connectors import SMBusConnection
import threading
import logging
from vosekast_control.Log import LOGGER
from inspect import iscoroutinefunction
from asyncio import create_task, BaseEventLoop

from time import sleep
from vosekast_control.connectors.AppControl import AppControl

logger = logging.getLogger(LOGGER)


class Callback:
    callback: Callable[[bool], None]
    input_pin: int

    def __init__(self, callback, input_pin) -> None:
        self.callback = callback
        self.input_pin = input_pin


class DigitalInputReaderConnector:
    callbacks: Dict[int, Callback]
    address: int
    counter: int
    event_loop: Optional[BaseEventLoop]

    def __init__(self, address=0x39):
        self.address = address
        self.counter = 0
        self.callbacks = {}
        self.old_state = None
        self._thread = threading.Thread(target=self._loop)
        self.event_loop = None

    def start(self):
        logger.info("Start background thread for DigitalInputs.")
        self._thread.start()

    def _loop(self):
        while not AppControl.is_terminating():
            try:
                new_state = self._read_state()

                if self.old_state is not None and new_state != self.old_state:
                    self._trigger_callbacks(new_state)

                self.old_state = new_state

                sleep(0.1)
            except Exception as err:
                logger.warning(f'Error in digital input loop: {err}')

        logger.info("Stopped background thread for DigitalInputs.")

    def _trigger_callbacks(self, new_state):
        for i in range(1, 8):
            pin_state = self._get_pin_state(i, new_state)
            if pin_state != self._get_pin_state(i, self.old_state):
                callback = self.callbacks.get(i)

                if callback is not None:
                    if (iscoroutinefunction(callback.callback)):
                        if self.event_loop is None:
                            logger.warning('DigitalInputReader tries to run a async task, but has no event loop reference.')
                    
                        self.event_loop.create_task(callback.callback(pin_state))
                    else:
                        callback.callback(pin_state)

    def _get_pin_state(self, pin, bin_state):
        pin_state = 1 ^ (1 & (bin_state >> (pin - 1)))
        return pin_state == 1

    def _read_state(self) -> int:
        state_reading = SMBusConnection.smbus.read_byte(self.address)
        return state_reading

    def digital_read(self, pin: int) -> bool:
        if pin >= 9 or pin <= 0:
            raise Exception("Pin is out of Range. Valid Pins are 1-8")

        bin_state = self._read_state()
        pin_state = 1 ^ (1 & (bin_state >> (pin - 1)))
        return pin_state == 1

    def add_callback(self, input_pin: int, callback: Callable[[bool], None]):
        callback_obj = Callback(callback, input_pin)
        self.callbacks[input_pin] = callback_obj

    def clear_callback(self, input_pin: int):
        del self.callbacks[input_pin]

    def clear_callbacks(self):
        self.callbacks = {}


DigitalInputReader = DigitalInputReaderConnector()
