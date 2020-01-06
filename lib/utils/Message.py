from datetime import datetime
import json


class Message:
    type = 'default'

    def __init__(self):
        self.timestamp = datetime.now()

    def get_json(self):
        return json.dumps(self.get_message_object)

    @property
    def get_message_object(self):
        return {
            'type': self.type,
        }


class ErrorMessage(Message):
    type: 'error'

    def __init__(self, message):
        super().__init__()

        self.message = message

    @property
    def get_message_object(self):
        message_object = super().get_message_object
        message_object['message'] = self.message

        return message_object


class SystemMessage(ErrorMessage):
    type = 'system'

    def __init__(self):
        super().__init__()


class StatusMessage(Message):
    type = 'status'

    def __init__(self, sensor_id, value, unit):
        super().__init__()

        self.sensor_id = sensor_id
        self.value = value
        self.unit = unit

    @property
    def topic(self):
        return f'status/{self.sensor_id}'

    @property
    def get_message_object(self):
        message_object = super().get_message_object
        message_object['sensor_id'] = self.sensor_id
        message_object['value'] = self.value
        message_object['unit'] = self.unit

        return message_object


class Command(Message):
    type = 'command'

    def __init__(self, description, state):
        super().__init__()

        self.description = description
        self.state = state

    @property
    def get_message_object(self):
        message_object = super().get_message_object
        message_object['description'] = self.description
        message_object['state'] = self.state

        return message_object
