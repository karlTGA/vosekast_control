from gmqtt import Client as MQTTClient


class MQTTController():

    def __init__(self, host):
        self.client = MQTTClient("client-id")
        self.host = host
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.client.on_subscribe = self.on_subscribe

    async def connect(self):
        await self.client.connect(self.host)

    async def disconnect(self):
        await self.client.disconnect()

    def publish(self, topic, message):
        self.client.publish(topic, message, qos=1)

    def on_connect(self, client, flags, rc, properties):
        print('Connected')
        self.client.subscribe('TEST/#', qos=0)

    def on_message(self, client, topic, payload, qos, properties):
        print('RECV MSG:', payload)

    def on_disconnect(self, client, packet, exc=None):
        print('Disconnected')

    def on_subscribe(self, client, mid, qos):
        print('SUBSCRIBED')
