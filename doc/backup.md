balenafin /boot/config.txt

dtoverlay=balena-fin-updated

changed to

dtoverlay=pi3-miniuart-bt

https://spellfoundry.com/2016/05/29/configuring-gpio-serial-port-raspbian-jessie-including-pi-3-4/
https://www.raspberrypi.org/documentation/configuration/uart.md

cat /dev/ttyS0 shows:

```
pi@raspberrypi:~ $ cat /dev/serial0

cd vos  
▒▒▒▒▒0.000▒▒砍
▒▒▒▒▒0.000▒▒砍
▒▒▒▒▒0.000▒▒砍
▒▒▒▒▒0.000▒▒砍
▒▒▒▒▒0.000▒▒砍
▒▒▒▒▒0.000▒▒砍
▒▒▒▒▒0.000▒▒砍
▒▒▒▒▒0.000▒▒砍
+▒▒▒▒0.000▒▒砍
+▒▒▒▒0.000▒▒砍
+▒▒▒▒0.000▒▒砍
+▒▒▒▒0.000▒▒砍
+▒▒▒▒0.000▒▒砍
```


ls -l /dev