# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['vosekast_control', 'vosekast_control.connectors', 'vosekast_control.utils']

package_data = \
{'': ['*']}

install_requires = \
['gmqtt>=0.6.2,<0.7.0', 'pendulum>=2.0.5,<3.0.0', 'pyserial>=3.4,<4.0']

extras_require = \
{':platform_machine != "armv7l"': ['rpi @ '
                                   'git+https://github.com/nosix/raspberry-gpio-emulator/@master'],
 ':platform_machine == "armv7l"': ['RPi.GPIO>=0.7.0,<0.8.0'],
 ':sys_platform == "linux"': ['uvloop>=0.14.0,<0.15.0']}

entry_points = \
{'console_scripts': ['dev = vosekast_control.scripts:dev',
                     'dev_backend = vosekast_control.scripts:dev_backend',
                     'dev_frontend = vosekast_control.scripts:dev_frontend']}

setup_kwargs = {
    'name': 'vosekast-control',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Karl Wolffgang',
    'author_email': 'karl_eugen.wolffgang@tu-dresden.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7',
}


setup(**setup_kwargs)
