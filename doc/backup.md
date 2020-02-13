## dev/ttyS0:

dev/ttyS0 not working,changed to use dev/serial0 softlink

https://spellfoundry.com/2016/05/29/configuring-gpio-serial-port-raspbian-jessie-including-pi-3-4/
https://www.raspberrypi.org/documentation/configuration/uart.md

### read scale output:

```
cat /dev/serial0
```

### show devices:

```
ls -l /dev
```
