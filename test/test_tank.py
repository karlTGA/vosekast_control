from vosekast_control.Tank import Tank
from unittest.mock import MagicMock
import pytest
from datetime import datetime


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
        self.vosekast = vosekast

        return tank

    def test_init(self, tank: Tank):
        assert isinstance(tank, Tank)
        assert tank.state == tank.UNKNOWN

    def test_drain_tank(self, tank: Tank):
        tank.drain_tank()

        assert tank.state == tank.IS_DRAINING

    def test_prepare_to_fill(self, tank: Tank):
        tank.prepare_to_fill()

        assert self.drain_valve.close.called

    @pytest.mark.asyncio
    async def test_fill(self, tank: Tank):
        await tank.fill()
        assert self.vosekast.prepare_measuring.called
        assert datetime.now.called
        assert self.logger.called

    def test__on_draining(self, tank: Tank):
        tank._on_draining()
        assert tank.state == tank.IS_DRAINING

    def test__on_full(self, tank: Tank):
        tank._on_full()
        assert tank.state == tank.FILLED

    def test__handle_drained(self, tank: Tank):
        tank._handle_drained()
        assert tank.state == tank.DRAINED

    def test__handle_filling(self, tank: Tank):
        tank._handle_filling()
        assert tank.state == tank.IS_FILLING

    def test_state(self, tank: Tank):
        tank.state = tank.EMPTY
        assert tank.state == tank.EMPTY

    def test_publish_state(self, tank: Tank):
        tank.publish_state()
