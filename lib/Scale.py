from PyQt5.QtCore import pyqtSignal, QObject
import serial

class Scale(QObject):

    def __init__(self, port='/dev/ttyS0', baudrate=9600, bytesize=serial.SEVENBITS, timeout=1):
        super().__init__()

        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.timeout = timeout
        self.connection = None
        self.last_values = []

    def open_connection(self):
        ser = serial.Serial()
        ser.port = self.port
        ser.baudrate = self.baudrate
        ser.bytesize = self.bytesize
        ser.timeout = self.timeout

        self.connection = ser
        self.connection.open()

    def start_measurement_thread(self):
        pass

