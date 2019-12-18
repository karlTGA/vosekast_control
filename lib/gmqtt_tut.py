import asyncio
from MQTT import MQTTController
import uvloop
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


async def main():
    host = 'localhost'
    token = None

    controller = MQTTController(host)

    await controller.connect()
    await asyncio.sleep(1)

    if token != None:
        controller.set_credentials(username, password)

    message = "Nachricht"
    topic = "TEST/TEST"

    controller.publish(topic, message)

    await asyncio.sleep(5)

    await controller.disconnect()


if __name__ == '__main__':
    asyncio.run(main())
