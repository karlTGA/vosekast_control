from datetime import datetime
import json
from logging import LogRecord
import logging
from typing import List, Dict


class Message:
    type = "default"

    def __init__(self):
        self.timestamp = datetime.now().isoformat()

    def get_json(self):
        return json.dumps(self.get_message_object())

    def get_message_object(self):
        return {"type": self.type, "time": self.timestamp}


class LogMessage(Message):
    type = "log"

    def __init__(self, record: LogRecord):
        super().__init__()

        self.record = record
        self.sensor_id = record.module

    def get_message_object(self):
        message_object = super().get_message_object()
        message_object["sensor_id"] = self.sensor_id
        message_object["message"] = self.record.message
        message_object["level"] = self.record.levelname

        if (
            self.record.levelno == logging.ERROR
            or self.record.levelno == logging.CRITICAL
        ):
            message_object["type"] = self.record.levelname

        return message_object

    @property
    def level(self):
        return self.record.levelno

    @property
    def topic(self):

        if (
            self.record.levelno == logging.ERROR
            or self.record.levelno == logging.CRITICAL
        ):
            return f"vosekast/error/{self.sensor_id}"

        else:
            return "vosekast/log"


class StatusMessage(Message):
    type = "status"

    def __init__(
        self, device_type: str, device_id: str, new_state: str, properties: Dict = {}
    ):
        super().__init__()

        self.device_type = device_type  # could be 'pump', 'scale' ...
        self.device_id = device_id  # for example measuring_tank_pump
        self.new_state = new_state  # use string with unit
        self.properties = properties

    @property
    def topic(self):
        return f"vosekast/status/{self.device_type}/{self.device_id}"

    def get_message_object(self):
        message_object = super().get_message_object()
        message_object["device_type"] = self.device_type
        message_object["device_id"] = self.device_id
        message_object["new_state"] = self.new_state

        if "run_id" in self.properties:
            message_object["run_id"] = self.properties["run_id"]

        return message_object


class InfoMessage(Message):
    type = "info"

    def __init__(self, system: str, info: object):
        super().__init__()

        self.system = system  # could be 'testrun_controlle', 'testrun'
        self.info = info  # the new info as object

    @property
    def topic(self):
        return f"vosekast/info/{self.system}"

    def get_message_object(self):
        message_object = super().get_message_object()
        message_object["id"] = self.system
        message_object["payload"] = self.info

        return message_object


class DataMessage(Message):
    type = "data"

    def __init__(self, data_type: str, identifier: str, payload: List[tuple]):
        super().__init__()

        self.data_type = data_type
        self.id = identifier
        self.payload = payload

    @property
    def topic(self):
        return f"vosekast/data/{self.id}"

    def get_message_object(self):
        message_object = super().get_message_object()
        message_object["id"] = self.id
        message_object["dataType"] = self.data_type
        message_object["payload"] = self.payload

        return message_object


# class Command(Message):
#     type = "command"

#     def __init__(self, sensor_id, description, state):
#         super().__init__()

#         self.sensor_id = sensor_id
#         self.description = description
#         self.state = state

#     @property
#     def topic(self):
#         return f"vosekast/command/{self.sensor_id}"

#     def get_message_object(self):
#         message_object = super().get_message_object()
#         message_object["sensor_id"] = self.sensor_id
#         message_object["description"] = self.description
#         message_object["state"] = self.state

#         return message_object
