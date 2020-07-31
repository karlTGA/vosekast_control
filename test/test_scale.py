from vosekast_control.Scale import Scale
import pytest


class TestScale:
    @pytest.fixture
    def scale(self):
        instance = Scale(name="TestScale", emulate=True)
        return instance

    def test_init(self, scale):
        assert isinstance(scale, Scale)

    @pytest.mark.asyncio
    async def test_start_and_stop(self, scale):
        scale.start()
        assert scale.state == scale.RUNNING

        await scale.stop()
        assert scale.state == scale.STOPPED
