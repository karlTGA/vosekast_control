balenafin config.txt


dtparam=audio=on
dtoverlay=balena-fin-updated
enable_uart=1

changed to

dtoverlay=pi3-miniuart-bt

https://spellfoundry.com/2016/05/29/configuring-gpio-serial-port-raspbian-jessie-including-pi-3-4/
https://www.raspberrypi.org/documentation/configuration/uart.md
cat /dev/ttyS0