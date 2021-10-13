from vosekast_control.Valve import Valve
from unittest.mock import MagicMock
import pytest


class TestValve:
    @pytest.fixture
    def valve(self):
        vosekast = MagicMock()
        control_pin = 13
        valve_type = Valve.TWO_WAY
        regulation = Valve.BINARY

        valve = Valve(vosekast, "test_valve", control_pin, valve_type, regulation)

        return valve

    def test_init(self, valve: Valve):
        assert isinstance(valve, Valve)
        assert valve.state == valve.UNKNOWN

    def test_open(self, valve: Valve):
        valve.open()

        assert valve.state == valve.OPEN

    def test_close(self, valve: Valve):
        valve.close()

        assert valve.state == valve.CLOSED

    def test_is_open(self, valve: Valve):
        valve.close()
        assert not valve.is_open

    def test_is_closed(self, valve: Valve):
        valve.open()
        assert not valve.is_closed

    def test_state(self, valve: Valve):
        valve.state = valve.OPEN
        assert valve.state == valve.OPEN

    def test_publish_state(self, valve: Valve):
        valve.publish_state()
