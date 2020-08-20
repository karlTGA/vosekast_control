from vosekast_control.connectors.RelayControl import RelayControlConnector
import pytest
from vosekast_control.connectors import SMBusConnection


class TestRelayControl:
    @pytest.fixture
    def relay_control(self):
        SMBusConnection.init_bus(emulate=True)

        return RelayControlConnector()

    def test_init(self, relay_control: RelayControlConnector):
        assert isinstance(relay_control, RelayControlConnector)
        assert relay_control.address == 0x38
        assert relay_control.state_binary == 255

    def test_all_on(self, relay_control: RelayControlConnector):
        relay_control.all_on()
        assert relay_control.state_binary == 0

    def test_all_off(self, relay_control: RelayControlConnector):
        relay_control.all_on()
        assert relay_control.state_binary == 0
        relay_control.all_off()
        assert relay_control.state_binary == 255

    def test_relays_on(self, relay_control: RelayControlConnector):
        relay_control.relays_on([2, 5])
        assert relay_control.state_binary == 237

    def test_read_state(self, relay_control: RelayControlConnector):
        relay_control.relays_on([2, 4])
        state = relay_control.read_state()

        assert state == 245

    def test_get_state_dict(self, relay_control: RelayControlConnector):
        relay_control.relays_on([1, 6])
        state_dict = relay_control.get_state_dict()

        assert relay_control.state_binary == 222
        assert state_dict[1] is True
        assert state_dict[2] is False
        assert state_dict[5] is False
        assert state_dict[6] is True
        assert state_dict[7] is False
