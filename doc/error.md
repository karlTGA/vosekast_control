# current error messages, needs work:

## Bounce:
```
2020-03-12 09:52:45,555 - INFO - TestSequence - Initialising sequence.
2020-03-12 09:52:45,556 - DEBUG - Vosekast - New Vosekast state is: PREPARING MEASUREMENT
2020-03-12 09:52:45,557 - DEBUG - Scale - Waiting for thread_loop.
2020-03-12 09:52:45,558 - DEBUG - TestSequence - Scale running, continuing.
2020-03-12 09:52:45,558 - INFO - Tank - Measuring Tank state: UNKNOWN
2020-03-12 09:52:45,560 - INFO - Tank - Constant Tank state: UNKNOWN
2020-03-12 09:52:45,561 - INFO - Valve - Closing Measuring Drain Valve
2020-03-12 09:52:45,563 - DEBUG - Tank - No drain valve on the Constant Tank
2020-03-12 09:52:45,563 - INFO - Pump - Starting Pump Constant Tank
2020-03-12 09:52:45,565 - INFO - Pump - Stopping Pump Measuring Tank
2020-03-12 09:52:45,566 - DEBUG - Tank - 0.005224s < time allotted (90s)

# system seems to trigger alerts, why?

2020-03-12 09:52:46,022 - INFO - Tank - Measuring Tank is being filled.
2020-03-12 09:52:46,024 - INFO - Tank - Measuring Tank is being drained.
2020-03-12 09:52:46,025 - INFO - Tank - Constant Tank is being drained.
2020-03-12 09:52:46,027 - INFO - Tank - Constant Tank is drained.

# alerts have triggered callback function, which change Tank states

2020-03-12 09:52:46,568 - INFO - Tank - Measuring Tank state: IS_DRAINING
2020-03-12 09:52:46,570 - INFO - Tank - Constant Tank state: DRAINED

# fill function detects Tank state change and aborts

2020-03-12 09:52:46,571 - DEBUG - TestSequence - Vosekast not ready to measure.
```

## MQTT:

```
[ERROR HANDLE PKG]
Traceback (most recent call last):
  File "/home/pi/.local/share/virtualenvs/vosekast_control-pmETU7-i/lib/python3.7/site-packages/gmqtt/mqtt/handler.py", line 357, in __call__
    result = self._handle_packet(cmd, packet)
  File "/home/pi/.local/share/virtualenvs/vosekast_control-pmETU7-i/lib/python3.7/site-packages/gmqtt/mqtt/handler.py", line 210, in _handle_packet
    handler(cmd, packet)
  File "/home/pi/.local/share/virtualenvs/vosekast_control-pmETU7-i/lib/python3.7/site-packages/gmqtt/mqtt/handler.py", line 370, in _handle_suback_packet
    self.on_subscribe(self, mid, granted_qos)
TypeError: on_subscribe() missing 1 required positional argument: 'properties'
```
