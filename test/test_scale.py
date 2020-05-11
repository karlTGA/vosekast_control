from vosekast_control.Scale import Scale
from unittest.mock import MagicMock
import pytest


class TestScale:
    @pytest.fixture
    def scale(self):
        instance = Scale(name="TestScale", emulate=True)
        return instance

    def test_init(self, scale):
        assert isinstance(scale, Scale)

    def test_start(self, scale):
        scale.start()
        assert scale.state == scale.RUNNING

    @pytest.mark.asyncio
    async def test_stop(self, scale):
        scale.start()
        assert scale.state == scale.RUNNING

        await scale.stop()
        assert scale.state == scale.STOPPED
