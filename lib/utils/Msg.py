from datetime import datetime
import json
from logging import LogRecord


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


# class ErrorMessage(Message):
#     type = 'error'

#     def __init__(self, sensor_id, message):
#         super().__init__()

#         self.sensor_id = sensor_id
#         self.message = message

#     @property
#     def topic(self):
#         return f'vosekast/error/{self.sensor_id}'

#     def get_message_object(self):
#         message_object = super().get_message_object()
#         message_object['sensor_id'] = self.sensor_id
#         message_object['message'] = self.message

#         return message_object


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
        
        if self.record.levelname == "ERROR" or self.record.levelname == "CRITICAL":
            message_object['type'] = self.record.levelname

        return message_object

    @property
    def topic(self):
        
        if self.record.levelname == "ERROR" or self.record.levelname == "CRITICAL":
            return f'vosekast/error/{self.sensor_id}'
            
        else:
            return 'vosekast/log'


class StatusMessage(Message):
    type = 'status'

    def __init__(self, sensor_id, value, unit):
        super().__init__()

        self.sensor_id = sensor_id
        self.value = value
        self.unit = unit

    @property
    def topic(self):
        return f'vosekast/status/{self.sensor_id}'

    def get_message_object(self):
        message_object = super().get_message_object()
        message_object['sensor_id'] = self.sensor_id
        message_object['value'] = self.value
        message_object['unit'] = self.unit

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
