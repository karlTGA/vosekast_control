from datetime import datetime
import json
from gmqtt import Client as MQTTClient


class MQTTController():

    def __init__(self, host):
        self.client = MQTTClient("Vosekast")
        self.host = host
        self.topic = "vosekast/commands"
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.client.on_subscribe = self.on_subscribe

    async def connect(self):
        await self.client.connect(self.host)

    async def disconnect(self):
        await self.client.disconnect()

    @property
    def connected(self):
        return self.client.is_connected

    def publish(self, topic, message):
        self.client.publish(topic, message, qos=0)
        print("Published: \"" + message + "\" to topic: \"" + topic + "\"")

    def publish_message(self, message_object):
        self.publish(message_object.topic, message_object.get_json())

    def on_connect(self, client, flags, rc, properties):
        self.client.subscribe(self.topic, qos=0)
        if self.connected:
            print('Connected to host: \"' + self.host + "\"")

    def on_message(self, client, topic, payload, qos, properties):
        msg = json.loads(payload.decode("utf-8"))
        MQTTCommandHandler(msg)

        print('Received: \"' + msg + "\" from client: " + self.client._client_id)



    def on_disconnect(self, client, packet, exc=None):
        print('Disconnected')

    def on_subscribe(self, client, mid, qos):
        print('Vosekast listening on: \"' + self.topic + "\"")

    def set_credentials(self, username, password):
        self.client.set_auth_credentials(username, password)

    def connection_test(self):
        return self.client.is_connected

class MQTTCommandHandler():
    type = 'command'

    def __init__(self):
        pass

    # def read_message_object(self):
    #     return {
    #         'type': self.type,
    #         'description': self.description,
    #         'sensor_id': self.sensor_id,
    #         'state': self.state
    #     }
