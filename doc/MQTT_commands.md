# sending commands to Vosekast via MQTT

## exemplary message (json) with all required fields:

```json
{
	"type": "command",
	"timestamp": "2019-11-20T19:03:59.975Z+0100",
	"target": "valve",
	"target_id": "measuring_drain_valve",
	"command": "close",
	"data": null
} 
```
### needs to publish to topic: vosekast/commands

## modules and their respective commands:

* target = valve
    * target_id = Measuring Drain Valve, Measuring Tank Switch
        * command = open, close

```json
{
	"type": "command",
	"timestamp": "2019-11-20T19:03:59.975Z+0100",
	"target": "valve",
	"target_id": "measuring_tank_switch",
	"command": "open",
	"data": null
} 
```

* target = pump
    * target_id = Pump Constant Tank, Pump Measuring Tank
        * command = start, stop, toggle

```json
{
	"type": "command",
	"timestamp": "2019-11-20T19:03:59.975Z+0100",
	"target": "pump",
	"target_id": "pump_constant_tank",
	"command": "toggle",
	"data": null
} 
```

* target = tank
    * target_id = Constant Tank, Measuring Tank (only Measuring Tank has a drain valve)
        * command = drain_tank, prepare_to_fill

```json
{
	"type": "command",
	"timestamp": "2019-11-20T19:03:59.975Z+0100",
	"target": "tank",
	"target_id": "constant_tank",
	"command": "prepare_to_fill",
	"data": null
} 
```

* target = scale
    * target_id = scale
        * command = open_connection, close_connection, start_measurement_thread, stop_measurement_thread, read_value_from_scale, print_diagnostics
            * open/close_connection: self-explanatory
            * start/stop_measurement_thread: Starts/stops threads for reading scale data.
            * read_value_from_scale: Get current scale value.
            * print_diagnostics: Prints many diagnostics (not just scale). 

```json
{
	"type": "command",
	"timestamp": "2019-11-20T19:03:59.975Z+0100",
	"target": "scale",
	"target_id": "measuring_scale",
	"command": "print_diagnostics",
	"data": null
} 
```

* target = system
    * target_id = system
        * command = shutdown, clean, prepare_measuring, ready_to_measure, start_sequence, stop_sequence, pause_sequence, continue_sequence, empty_tanks
            * shutdown: Shutdown vosekast, including Raspberry Pi.
            * clean: Stops all pumps, drains the Measuring Tank and closes scale connection.
            * start/stop/pause/continue_sequence: Start will first fill the Constant Tank and then start measuring. If there is no scale connection it will first be initialised.
            * prepare_measuring: Close drain valve, start Pump Constant Tank
            * ready_to_measure: Return whether vosekast ready to measure
            * empty_tanks: Command to empty both Measuring and Constant Tank. Be aware that the Stock Tank is likely to overflow.

```json
{
	"type": "command",
	"timestamp": "2019-11-20T19:03:59.975Z+0100",
	"target": "system",
	"target_id": "system",
	"command": "start_sequence",
	"data": null
} 
```        

commands with (*) do not fully work as of now

if target, target_id or command do not match, a respective error message will be thrown.