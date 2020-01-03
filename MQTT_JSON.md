# MQTT and JSON

The MQTT protocol is used to send commands to Vosekast as well as to publish sensor data.
We decided to use the JSON:API for its ease of use, flexibility and lightweight design to encode and decode all MQTT messages.

## JSON payload format

* There will be different classes to distinguish between sensor data/commands/error messages. Each class will publish to a separate topic for easier differentiation.
	* All sensors publish to topic /status. 
	* Commands will be published to /commands.
	* System messages will publish to /system
	* Error messages publish to /error.
* Data is distinguished by sensor_id.

```json

{
	"type": "sensor data",
	"sensor_id": "z.B. Tank_Fuellstand",
	"timestamp": "2019-11-20T19:02:59.975Z+0100", 
	"value": 99
},
{
	"type": "sensor data",
	"sensor_id": "Temperatur Tank",
	"timestamp": "2019-11-20T19:02:59.975Z+0100", 
	"temperature": 24.59
}
```

### Resources:

* http://www.steves-internet-guide.com/send-json-data-mqtt-python/
* http://www.steves-internet-guide.com/mqtt-topic-payload-design-notes/
* https://stackoverflow.com/questions/42731998/how-to-publish-json-data-on-mqtt-broker-in-python
* http://support.elmark.com.pl/advantech/pdf/bb/MQTT_Topics_and_JSON_Data_Format.pdf
* https://owntracks.org/booklet/tech/json/
* https://www.pikkerton.de/_mediafiles/133-mqtt-payload-data.pdf
* https://com2m.de/blog/technology/message-payloads-json-vs-byte-protocol-in-conjunction-with-compression/
