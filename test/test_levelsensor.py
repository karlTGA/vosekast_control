from vosekast_control.LevelSensor import LevelSensor
from unittest.mock import MagicMock
import pytest
import asyncio
import json



class TestLevelSensor:
    @pytest.fixture
    def levelsensor(self):
        vosekast = MagicMock()
        gpio_controller = MagicMock()
        control_pin = 13
        levelsensor_type = bool
        regulation = LevelSensor.HIGH
        extra_callback_function = MagicMock()

        levelsensor = LevelSensor("test_levelsensor", control_pin, levelsensor_type, regulation, gpio_controller)
        
        self.extra_callback_function = extra_callback_function
        self._gpio_controller = gpio_controller

        return levelsensor

    def test_init(self, levelsensor: LevelSensor):
        assert isinstance(levelsensor, LevelSensor)
        assert self._gpio_controller.setup.called
        assert self._gpio_controller.add_event_detect.called

    def test_add_callback(self, levelsensor: LevelSensor):
        levelsensor.add_callback(self.test_callback_function())

        assert self.extra_callback_function.called

    def test_callback_function(self):
        pass

    def test_clear_callbacks(self, levelsensor: LevelSensor):
        levelsensor.clear_callbacks()

        assert self._gpio_controller.remove_event_detect.called
        assert self._gpio_controller.add_event_detect.called

    def test_state(self, levelsensor: LevelSensor):
        assert self._gpio_controller.input.called

    def test_publish_state(self, levelsensor: LevelSensor):
        levelsensor.publish_state()

        assert MQTTConnection.publish_message.called

