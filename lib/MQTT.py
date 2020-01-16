import json
from gmqtt import Client as MQTTClient


def noop(*args, **kwargs):
    pass


class MQTTController():

    def __init__(self, host):
        self.client = MQTTClient("Vosekast")
        self.host = host
        self.on_command = noop
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
        # print("Published: \"" + message + "\" to topic: \"" + topic + "\"")

    def publish_message(self, message_object):
        self.publish(message_object.topic, message_object.get_json())

    def on_connect(self, client, flags, rc, properties):
        self.client.subscribe(self.topic, qos=0)
        if self.connected:
            print('Connected to host: \"' + self.host + "\"")

    async def on_message(self, client, topic, payload, qos, properties):
        message = payload

        try:
            command = json.loads(message)

            if command['type'] == 'command':
                await self.on_command(command)

        except ValueError:
            print("unexpected formatting: " +
                  str(payload.decode("utf-8")))
        except KeyError:
            print("Got message without type.")

        # print('Received: \"' + str(payload.decode("utf-8")) + "\" from client: " + self.client._client_id)

    def on_disconnect(self, client, packet, exc=None):
        print('Disconnected')

    def on_subscribe(self, client, mid, qos):
        print('Vosekast listening on: \"' + self.topic + "\"")

    def set_credentials(self, username, password):
        self.client.set_auth_credentials(username, password)

    def connection_test(self):
        return self.client.is_connected