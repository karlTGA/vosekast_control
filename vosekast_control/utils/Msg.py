from datetime import datetime
import json
from logging import LogRecord
import logging


class Message:
    type = 'default'

    def __init__(self):
        self.timestamp = datetime.now().isoformat()

    def get_json(self):
        return json.dumps(self.get_message_object())

    def get_message_object(self):
        return {
            'type': self.type,
            'time': self.timestamp
        }


class LogMessage(Message):
    type = 'log'

    def __init__(self, record: LogRecord):
        super().__init__()

        self.record = record
        self.sensor_id = record.module

    def get_message_object(self):
        message_object = super().get_message_object()
        message_object['sensor_id'] = self.sensor_id
        message_object['message'] = self.record.message
        message_object['level'] = self.record.levelname

        if self.record.levelno == logging.ERROR or self.record.levelno == logging.CRITICAL:
            message_object['type'] = self.record.levelname

        return message_object

    @property
    def level(self):
        return self.record.levelno

    @property
    def topic(self):

        if self.record.levelno == logging.ERROR or self.record.levelno == logging.CRITICAL:
            return f'vosekast/error/{self.sensor_id}'

        else:
            return 'vosekast/log'


class StatusMessage(Message):
    type = 'status'

    def __init__(self, sensor_id, value1, unit1, value2, unit2):
        super().__init__()

        self.sensor_id = sensor_id
        self.value1 = value1
        self.unit1 = unit1
        self.value2 = value2
        self.unit2 = unit2

    @property
    def topic(self):
        return f'vosekast/status/{self.sensor_id}'

    def get_message_object(self):
        message_object = super().get_message_object()
        message_object['sensor_id'] = self.sensor_id
        message_object['value1'] = self.value1
        message_object['unit1'] = self.unit1
        message_object['value2'] = self.value2
        message_object['unit2'] = self.unit2

        return message_object


class Command(Message):
    type = 'command'

    def __init__(self, sensor_id, description, state):
        super().__init__()

        self.sensor_id = sensor_id
        self.description = description
        self.state = state

    @property
    def topic(self):
        return f'vosekast/command/{self.sensor_id}'

    def get_message_object(self):
        message_object = super().get_message_object()
        message_object['sensor_id'] = self.sensor_id
        message_object['description'] = self.description
        message_object['state'] = self.state

        return message_object
