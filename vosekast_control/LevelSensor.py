from asyncio.base_events import BaseEventLoop
from typing import Awaitable, Callable, Generator, Optional, Union
from vosekast_control.connectors import MQTTConnection
from vosekast_control.utils.Msg import StatusMessage
from vosekast_control.connectors.DigitalInputReader import DigitalInputReader
import logging
import asyncio
from inspect import iscoroutinefunction

from vosekast_control.Log import LOGGER

logger = logging.getLogger(LOGGER)


class LevelSensor:
    # Positions
    HIGH = "HIGH"
    LOW = "LOW"
    name: str
    sensor_type: str
    position: str
    _input_pin: int
    on_change: Optional[Callable[[bool], Union[Generator[None, None, None], Awaitable[None]]]]
    event_loop: BaseEventLoop

    def __init__(self, name, input_pin, sensor_type, position, on_change=None):
        self.name = name
        self.sensor_type = sensor_type
        self.position = position
        self._input_pin = input_pin
        self.on_change = on_change
        self.event_loop = asyncio.get_event_loop()

        self._add_callback(self.handle_change)

    def __del__(self):
        self._clear_callback()

    @property
    def state(self):
        return DigitalInputReader.digital_read(self._input_pin)

    def handle_change(self, is_triggered: bool):
        new_state = "triggered" if is_triggered else "untriggered"
        MQTTConnection.publish_message(
            StatusMessage("level_sensor", self.name, new_state)
        )

        if (self.on_change is None):
            return

        if (iscoroutinefunction(self.on_change)):
            self.event_loop.create_task(self.on_change(is_triggered))
        else:
            self.on_change(is_triggered)

    def _add_callback(self, callback: Callable[[bool], None]):
        if self._input_pin in DigitalInputReader.callbacks:
            logger.warning("It is not possible to add two callbacks for a levelsensor.")

        DigitalInputReader.add_callback(self._input_pin, callback)

    def _clear_callback(self):
        DigitalInputReader.clear_callback(self._input_pin)
        self._callback_id = None
