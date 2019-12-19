
from gmqtt import Client as MQTTClient


class MQTTController():

    def __init__(self, host):
        self.client = MQTTClient("Vosekast")
        self.host = host
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

    def on_connect(self, client, flags, rc, properties):
        self.client.subscribe('TEST/#', qos=0)
        if self.connected:
            print('Connected to: ' + self.host)

    def on_message(self, client, topic, payload, qos, properties):
        msg = str(payload.decode("utf-8"))
        print('Received: \"' + msg + "\" from client: " + self.client._client_id)

    def on_disconnect(self, client, packet, exc=None):
        print('Disconnected')

    def on_subscribe(self, client, mid, qos):
        print('Subscribed OK ' + str(mid))

    def set_credentials(self, username, password):
        self.client.set_auth_credentials(username, password)
