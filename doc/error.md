# program runs fine when emulated, but otherwise running python3 main.py will raise:

## Poetry on Balenafin:
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
