from vosekast_control.Pump import Pump
from unittest.mock import MagicMock
import pytest


class TestPump:
    @pytest.fixture
    def pump(self):
        vosekast = MagicMock()
        gpio_controller = MagicMock()
        control_pin = 12

        pump = Pump(vosekast, "test_pump", control_pin, gpio_controller)

        return pump

    def test_init(self, pump: Pump):
        assert isinstance(pump, Pump)
        assert pump.state == pump.UNKNOWN

    def test_start(self, pump: Pump):
        pump.start()

        assert pump.state == pump.RUNNING

    def test_stop(self, pump: Pump):
        pump.stop()

        assert pump.state == pump.STOPPED

    def test_toggle(self, pump: Pump):
        pump.start()
        pump.toggle()

        assert pump.state == pump.STOPPED

    def test_is_stopped(self, pump: Pump):
        pump.start()
        assert not pump.is_stopped

    def test_is_running(self, pump: Pump):
        pump.start()
        assert pump.is_running

    def test_state(self, pump: Pump):
        pump.state = pump.RUNNING
        assert pump.state == pump.RUNNING

    def test_publish_state(self, pump: Pump):
        pump.publish_state()
