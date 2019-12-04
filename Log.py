import logging
from PyQt5.QtCore import pyqtSignal, QObject

LOGGER = "ROOT"


class StatusBoxHandle(logging.Handler):
    def __init__(self, window):
        super().__init__()

        self.window = window
        self.log_message_handler = LogMessageToStatusBar(
            self.window.send_status_message
        )

    def emit(self, record):
        log_entry = self.format(record)
        self.log_message_handler.new_log_message(log_entry)


class LogMessageToStatusBar(QObject):
    """
    If we want send messages to the qt_gui, we have to use the signal slot process.
    """

    log_message = pyqtSignal(str, name="LogMessage")

    def __init__(self, slot):
        super().__init__()
        self.slot = slot
        self.log_message.connect(self.slot)

    def new_log_message(self, message):
        self.log_message.emit(message)


def setup_custom_logger():
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(levelname)s - %(module)s - %(message)s"
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(LOGGER)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger


def add_status_box_handler(window):
    handler = StatusBoxHandle(window)
    logger = logging.getLogger(LOGGER)
    logger.addHandler(handler)
