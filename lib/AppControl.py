class AppControl:
    """
    This class controls the hole app. Every thread should get the instance.
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
