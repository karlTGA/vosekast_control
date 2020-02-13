# program runs fine when emulated, but otherwise running python3 main.py will raise:

## Pi4:
```

2020-02-12 09:41:15,170 - INFO - Scale - Opening connection to scale.
[CONNACK] 0x1
2020-02-12 09:41:15,186 - DEBUG - Vosekast - Vosekast started ok.
2020-02-12 09:41:15,188 - INFO - Scale - Start measuring with scale.
TrueDisconnected

2020-02-12 09:41:16,192 - INFO - Scale - Measured b''
Exception in thread Thread-2:
Traceback (most recent call last):
  File "/usr/lib/python3.7/threading.py", line 917, in _bootstrap_inner
    self.run()
  File "/usr/lib/python3.7/threading.py", line 865, in run
    self._target(*self._args, **self._kwargs)
  File "/home/pi/vosekast_control/lib/Scale.py", line 87, in loop
    self.scale_history.appendleft(self.timestamp)
AttributeError: 'Scale' object has no attribute 'timestamp'

Connected to host: "localhost"
[ERROR HANDLE PKG]
Traceback (most recent call last):
  File "/home/pi/.local/share/virtualenvs/vosekast_control-pmETU7-i/lib/python3.7/site-packages/gmqtt/mqtt/handler.py", line 357, in __call__
    result = self._handle_packet(cmd, packet)
  File "/home/pi/.local/share/virtualenvs/vosekast_control-pmETU7-i/lib/python3.7/site-packages/gmqtt/mqtt/handler.py", line 210, in _handle_packet
    handler(cmd, packet)
  File "/home/pi/.local/share/virtualenvs/vosekast_control-pmETU7-i/lib/python3.7/site-packages/gmqtt/mqtt/handler.py", line 381, in _handle_suback_packet
    self.on_subscribe(self, mid, granted_qoses, properties)
TypeError: on_subscribe() takes 4 positional arguments but 5 were given

```
## Balenafin:
```

2020-02-12 12:47:49,485 - INFO - Scale - Opening connection to scale.
[CONNACK] 0x1
2020-02-12 12:47:49,501 - DEBUG - Vosekast - Vosekast started ok.
Disconnected
2020-02-12 12:47:49,503 - INFO - Scale - Start measuring with scale.
True
[EXC OCCURED] in reconnect future None
2020-02-12 12:47:49,506 - INFO - Scale - Measured b'\xb7 kg \r\n'
Exception in thread Thread-2:
Traceback (most recent call last):
  File "/usr/local/lib/python3.7/threading.py", line 917, in _bootstrap_inner
    self.run()
  File "/usr/local/lib/python3.7/threading.py", line 865, in run
    self._target(*self._args, **self._kwargs)
  File "/home/pi/vosekast_control/lib/Scale.py", line 87, in loop
    self.scale_history.appendleft(self.timestamp)
AttributeError: 'Scale' object has no attribute 'timestamp'

[EXC OCCURED] in reconnect future None
Connected to host: "localhost"
Vosekast listening on: "vosekast/commands"

```

```
2020-02-12 12:52:24,973 - INFO - Scale - Opening connection to scale.
[CONNACK] 0x1
2020-02-12 12:52:24,989 - DEBUG - Vosekast - Vosekast started ok.
2020-02-12 12:52:24,990 - INFO - Scale - Start measuring with scale.
True
Disconnected
[EXC OCCURED] in reconnect future None
2020-02-12 12:52:25,102 - INFO - Scale - Measured b'+    0.007 kg \r\n'
Exception in thread Thread-2:
Traceback (most recent call last):
  File "/usr/local/lib/python3.7/threading.py", line 917, in _bootstrap_inner
    self.run()
  File "/usr/local/lib/python3.7/threading.py", line 865, in run
    self._target(*self._args, **self._kwargs)
  File "/home/pi/vosekast_control/lib/Scale.py", line 81, in loop
    new_value = self.read_value_from_scale()
  File "/home/pi/vosekast_control/lib/Scale.py", line 142, in read_value_from_scale
    new_value = "".join(splitted_line[:2])
TypeError: sequence item 0: expected str instance, bytes found

[EXC OCCURED] in reconnect future None
```

```

2020-02-13 08:31:57,780 - INFO - Scale - Opening connection to scale.
[CONNACK] 0x1
2020-02-13 08:31:57,829 - DEBUG - Vosekast - Vosekast started ok.
2020-02-13 08:31:57,830 - INFO - Scale - Start measuring with scale.
Disconnected
[EXC OCCURED] in reconnect future None
[EXC OCCURED] in reconnect future None
Connected to host: "localhost"
Vosekast listening on: "vosekast/commands"


line: b'+    0.019 kg \r\n'
splitted_line: [b'+', b'0.019', b'kg']
2020-02-13 09:09:57,006 - INFO - Scale - Measured b'+    0.019 kg \r\n'
splitted_line_formatted: b'0.019'
b'0.019'
new value, len == 3: b'0.019'
reached loop, new value not None
Exception in thread Thread-2:
Traceback (most recent call last):
  File "/usr/local/lib/python3.7/threading.py", line 917, in _bootstrap_inner
    self.run()
  File "/usr/local/lib/python3.7/threading.py", line 865, in run
    self._target(*self._args, **self._kwargs)
  File "/home/pi/vosekast_control/lib/Scale.py", line 86, in loop
    self.add_new_value(new_value)
  File "/home/pi/vosekast_control/lib/Scale.py", line 170, in add_new_value
    delta = self.scale_history[0] - self.scale_history[2]
TypeError: unsupported operand type(s) for -: 'str' and 'str'



```