from vosekast_control.connectors.DigitalInputReader import DigitalInputReaderConnector
import pytest
from vosekast_control.connectors import SMBusConnection


class TestRelayControl:
    @pytest.fixture
    def digital_input_reader(self):
        SMBusConnection.init_bus(emulate=True)

        return DigitalInputReaderConnector()

    def test_init(self, digital_input_reader: DigitalInputReaderConnector):
        assert isinstance(digital_input_reader, DigitalInputReaderConnector)
        assert digital_input_reader.address == 0x39

    def test_digital_read(self, digital_input_reader: DigitalInputReaderConnector):
        SMBusConnection.smbus._state = 222

        assert digital_input_reader.digital_read(1) == 1
        assert digital_input_reader.digital_read(2) == 0
        assert digital_input_reader.digital_read(6) == 1
