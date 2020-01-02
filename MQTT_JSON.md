# MQTT and JSON

MQTT is used to send commands to Vosekast as well as to publish sensor data.

We decided to use the JSON:API for its ease of use, flexibility and lightweight design to encode and decode all MQTT messages.

## JSON payload format

* There will be different classes to distinguish between error messages/sensor data/command. Each class will publish to a separate topic  for easier differentiation.
	* All sensors publish to topic /status. 
	* Commands will be published to topic /commands.
	* Error messages publish to /error.
* Data is distinguished by sensor_id.

```json
{
	"title": "sensor_id",
	"description": "sensor input data",
	"type": "object",
	"error": false,
	"message": "msg"
	"required": ["s","t"],
 	"properties":
		{
 		"s":	{"title":"Sequence Number","description":"A number incremented for every publish of sensor data.",
 				"type":"integer",",minimum":0,"maximum":9},
 		"t":	{"title":"Timestamp","description":"An ISO 8601 timestamp of the UTC time for the sensor reading.",
 				"type":"string","format":"date-time"},
		"ai1":	{"title":"Analog Input 1","description":"The value of analog input 1.",
 				"$ref":"#/definitions/ai_value"},
 		"do1":	{"title":"Digital Output 1","description":"The state of digital output 1.",
 				"$ref":"#/definitions/do_value"},
		"temp1":{"title":"Temperature Input 1","description":"The value of temperature input 1.",
 				"$ref":"#/definitions/temp_value"}
		}
	 "definitions": 
		{
 		"ai_value":{"type":"number"},
 		"di_value":{"oneOf":[{"type":"boolean"},{"type":"number"}]},
 		"do_value":{"type":"boolean"},
 		"temp_value":{"type":"number"},
 		}
}
```

### Resources:

* http://www.steves-internet-guide.com/send-json-data-mqtt-python/
* http://www.steves-internet-guide.com/mqtt-topic-payload-design-notes/
* https://stackoverflow.com/questions/42731998/how-to-publish-json-data-on-mqtt-broker-in-python
* http://support.elmark.com.pl/advantech/pdf/bb/MQTT_Topics_and_JSON_Data_Format.pdf
