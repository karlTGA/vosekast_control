import logging
from lib.utils.Msg import LogMessage

LOGGER = "ROOT"


class MQTTLoggingHandler(logging.Handler):
    def __init__(self, mqtt_client):
        super().__init__()

        self.mqtt = mqtt_client

    def emit(self, record):
        mqttmsg = LogMessage(record)
    
        if self.mqtt.connection_test() and mqttmsg.level != logging.DEBUG:
            self.mqtt.publish_message(mqttmsg)


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


def add_mqtt_logger_handler(mqtt):
    handler = MQTTLoggingHandler(mqtt)
    logger = logging.getLogger(LOGGER)
    logger.addHandler(handler)
