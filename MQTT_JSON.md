# MQTT and JSON

The MQTT protocol is used to send commands to Vosekast as well as to publish sensor data.
We decided to use the JSON:API for its ease of use, flexibility and lightweight design to encode and decode all MQTT messages.

## JSON payload format

* There are different classes to distinguish between sensor data/ logs/ commands/ error messages. Each class will publish to a separate topic under /vosekast for easier differentiation.
	* Sensors publish to their on topic under /status, i.e. vosekast/status/Stock_Tank 
	* All log events will publish to /log, i.e. vosekast/log
	* Error messages publish to /error, i.e. vosekast/error/Stock_Tank
	* Commands will be published to /command, i.e. vosekast/command/Stock_Tank
* Data is distinguished by sensor_id and timestamp.

```json

{
	"type": "status",
	"timestamp": "2019-11-20T19:03:59.975Z+0100",
	"sensor_id": "Tank",
	"value": 99,
	"unit": "%"
},
{
	"type": "log message",
	"timestamp": "2019-11-20T19:03:59.975Z+0100",
	"level": "DEBUG/INFO/WARNING/ERROR/CRITICAL",
	"message": "Vosekast shutting down."
},
{
	"type": "error message",
	"timestamp": "2019-11-20T19:03:59.975Z+0100",
	"sensor_id": "Durchflussmesser",
	"message": "Flow rate out of bounds."
},
{
	"type": "command",
	"timestamp": "2019-11-20T19:03:59.975Z+0100",
	"description": "Pumpe anschalten",
	"sensor_id": "Pumpe",
	"state": "on"
} 
```

### Resources:

* http://www.steves-internet-guide.com/send-json-data-mqtt-python/
* http://www.steves-internet-guide.com/mqtt-topic-payload-design-notes/
* https://stackoverflow.com/questions/42731998/how-to-publish-json-data-on-mqtt-broker-in-python
* https://owntracks.org/booklet/tech/json/
* https://www.pikkerton.de/_mediafiles/133-mqtt-payload-data.pdf
* https://com2m.de/blog/technology/message-payloads-json-vs-byte-protocol-in-conjunction-with-compression/
