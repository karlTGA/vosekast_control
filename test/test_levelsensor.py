from vosekast_control.LevelSensor import LevelSensor
import pytest
from vosekast_control.connectors.DigitalInputReader import DigitalInputReader


class TestLevelSensor:
    @pytest.fixture
    def levelsensor(self):
        control_pin = 6
        levelsensor_type = bool
        regulation = LevelSensor.HIGH

        levelsensor = LevelSensor(
            "test_levelsensor", control_pin, levelsensor_type, regulation,
        )

        return levelsensor

    def callback_function(self, pin_state: bool):
        pass

    def test_init(self, levelsensor: LevelSensor):
        assert isinstance(levelsensor, LevelSensor)

    def test_add_callback(self, levelsensor: LevelSensor):
        levelsensor.add_callback(self.callback_function)

        assert len(DigitalInputReader.callbacks) == 1
        DigitalInputReader.clear_callbacks()

    def test_clear_callbacks(self, levelsensor: LevelSensor):
        levelsensor.add_callback(self.callback_function)
        assert len(DigitalInputReader.callbacks) == 1

        levelsensor.clear_callback()
        assert len(DigitalInputReader.callbacks) == 0

    def test_state(self, levelsensor: LevelSensor):
        assert levelsensor.state

    def test_publish_state(self, levelsensor: LevelSensor):
        levelsensor.publish_state()
