from vosekast_control.Tank import Tank
from unittest.mock import MagicMock
import pytest
import asyncio


class TestTank:
    @pytest.fixture
    def tank(self):
        vosekast = MagicMock()
        level_sensor = MagicMock()
        drain_sensor = MagicMock()
        overflow_sensor = MagicMock()
        drain_valve = MagicMock()
        source_pump = MagicMock()
        tank = Tank(
            "test_tank",
            100,
            level_sensor,
            drain_sensor,
            overflow_sensor,
            drain_valve,
            source_pump,
            vosekast=self,
        )

        self.level_sensor = level_sensor
        self.drain_sensor = drain_sensor
        self.overflow_sensor = overflow_sensor
        self.drain_valve = drain_valve
        self.source_pump = source_pump

        return tank

    def test_init(self, tank: Tank):
        assert isinstance(tank, Tank)
        assert tank.state == tank.UNKNOWN

    def test_drain_tank(self, tank: Tank):
        tank.drain_tank()

        assert tank.state == tank.IS_DRAINING

    # todo what to check for?
    def test_prepare_to_fill(self, tank: Tank):
        tank.prepare_to_fill()

        assert self.drain_valve.close.called

    # todo what to check for?
    @pytest.fixture(scope="session")
    async def test_fill(self, tank: Tank):
        await tank.fill()
        assert not tank.state == tank.STOPPED

    # _on_draining
    # _on_full

    def test_state(self, tank: Tank):
        tank.state = tank.EMPTY
        assert tank.state == tank.EMPTY

    def test_publish_state(self, tank: Tank):
        tank.publish_state()
