from enum import Enum
from PyQt5.QtCore import pyqtSignal, QObject





class States(Enum):
    PAUSE = 0
    RUNNING = 1
    READY = 2
    STOP = 3

print(States.PAUSE.value)
print(States.PAUSE.name)

print(States(0).name)
