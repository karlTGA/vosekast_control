# sending commands to Vosekast via MQTT

## exemplary message (json) with all required fields:

```json
{
	"type": "command",
	"timestamp": "2019-11-20T19:03:59.975Z+0100",
	"target": "valve",
	"target_id": "Measuring Drain Valve",
	"command": "close",
	"data": null
} 
```
### needs to publish to topic: vosekast/commands

## modules and their respective commands:

* target = valve
    * target_id = Measuring Drain Valve, Measuring Tank Switch
        * command = open, close
* target = pump
    * target_id = Pump Constant Tank, Pump Measuring Tank
        * command = start, stop, toggle
* target = tank
    * target_id = Stock Tank, Constant Tank, Measuring Tank (only Measuring Tank has a drain valve)
        * command = drain_tank, prepare_to_fill
* target = scale
    * target_id = scale
        * command = open_connection, close_connection, start_measurement_thread, stop_measurement_thread, get_stable_value, read_value_from_scale, print_diagnostics
* target = system
    * target_id = system
        * command = shutdown, clean, prepare_measuring, ready_to_measure, start_sequence*, stop_sequence*

commands with (*) do not fully work as of now

if target, target_id or command do not match, a respective error message will be thrown.