# different pipfiles needed:

For some reason, setting markers in Pipfile does not work or raise errors (Pi). Until we can fix this, we need different Pipfiles.

## Pi:

```

[[source]]
name = "pypi"
url = "https://pypi.org/simple"
verify_ssl = true

[dev-packages]
pylint = "*"
rope = "*"
autopep8 = "*"

[packages]
pyserial = "*"
SIP = "*"
pydux = "*"
uvloop = "*"
gmqtt = "*"
"RPi.GPIO" = "*"
datetime = "*"

[requires]
python_version = "3.7"

[pipenv]
allow_prereleases = true

[scripts]
start = "python main.py"

[packages.raspberry-gpio-emulator]
editable = true
git = "https://github.com/nosix/raspberry-gpio-emulator"

```

## other:

```
[[source]]
name = "pypi"
url = "https://pypi.org/simple"
verify_ssl = true

[dev-packages]
pylint = "*"
rope = "*"
autopep8 = "*"

[packages]
pyserial = "*"
SIP = "*"
raspberry-gpio-emulator = {editable = true,git = "https://github.com/nosix/raspberry-gpio-emulator", sys_platform = "!= 'linux2'"}
pydux = "*"
uvloop = "*"
gmqtt = "*"
"RPi.GPIO" = {version = "*", sys_platform = "== 'RPI'"}

[requires]
python_version = "3.7"

[pipenv]
allow_prereleases = true

[scripts]
start = "python main.py"

[packages.raspberry-gpio-emulator]
editable = true
git = "https://github.com/nosix/raspberry-gpio-emulator"
```

# Pi backup:
```
[[source]]
name = "pypi"
url = "https://pypi.org/simple"
verify_ssl = true

[dev-packages]
pylint = "*"
rope = "*"
autopep8 = "*"

[packages]
pyserial = "*"
sip = "*"
pydux = "*"
uvloop = "*"
gmqtt = "*"
"RPi.GPIO" = "*"

[requires]
python_version = "3.7"

[pipenv]
allow_prereleases = true

[scripts]
start = "python main.py"

[packages.raspberry-gpio-emulator]
editable = true
git = "https://github.com/nosix/raspberry-gpio-emulator"

```
# Balenafin backup:
´´´
[[source]]
name = "pypi"
url = "https://pypi.org/simple"
verify_ssl = true

[dev-packages]
pylint = "*"
black = "*"
rope = "*"
autopep8 = "*"

[packages]
pyserial = "*"
SIP = "*"
raspberry-gpio-emulator = {editable = true,git = "https://github.com/nosix/raspberry-gpio-emulator"}
pydux = "*"
uvloop = "*"
gmqtt = "*"

[requires]
python_version = "3.7"

[pipenv]
allow_prereleases = true

[scripts]
start = "python main.py"

´´´