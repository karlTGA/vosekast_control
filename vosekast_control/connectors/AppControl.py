from vosekast_control.utils.Msg import StatusMessage
from vosekast_control.connectors import MQTTConnection


class _AppControl:
    """
    This class controls the whole app. Every thread should get the instance.
    """

    # states
    UNKNOWN = "UNKNOWN"
    INIT = "INIT"
    RUNNING = "RUNNING"
    SHUTDOWN = "SHUTDOWN"
    RESTART = "RESTART"
    STOPPED = "STOPPED"

    def __init__(self):
        self.state = self.INIT

    def start(self):
        self.state = self.RUNNING

    def shutdown(self):
        self.state = self.SHUTDOWN

    def stopped(self):
        self.state = self.STOPPED

    def is_terminating(self):
        return self.state in [self.STOPPED, self.SHUTDOWN, self.RESTART]

    @property
    async def state(self) -> str:
        return self._state

    @state.setter
    def state(self, new_state):
        MQTTConnection.publish_message(
            message_object=StatusMessage("system", "app_control", new_state)
        )
        self._state = new_state


AppControl = _AppControl()
