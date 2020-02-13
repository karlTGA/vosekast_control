import serial
from collections import deque
from threading import Thread
from time import sleep
import logging
from lib.Log import LOGGER
from random import uniform
from itertools import islice
from lib.utils.Msg import StatusMessage

from lib.EnumStates import States

from collections import deque
from datetime import datetime


class Scale:

    def __init__(
        self,
        vosekast,
        port="/dev/serial0",
        baudrate=9600,
        bytesize=serial.SEVENBITS,
        timeout=1,
        emulate=False,
    ):
        super().__init__()

        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.timeout = timeout
        self.connection = None
        self.last_values = deque([], 10)
        self.thread = Thread()
        self.emulate = emulate
        self.run = False
        self.timestamp = datetime.now()
        #self.publish = False
        self.stable = False
        self.logger = logging.getLogger(LOGGER)
        self.vosekast = vosekast
        self.state = States.NONE
        self.mqtt = self.vosekast.mqtt_client
        self.threads = []
        self.scale_history = deque([], maxlen=200)
        self.flow_history = deque([], maxlen=100)


    def open_connection(self):
        if not self.emulate:
            ser = serial.Serial()
            ser.port = self.port
            ser.baudrate = self.baudrate
            ser.bytesize = self.bytesize
            ser.timeout = self.timeout

            self.connection = ser
            self.connection.open()
            self.logger.info("Opening connection to scale.")
        else:
            self.logger.info("Emulating open_connection scale.")

    def close_connection(self):
        if not self.emulate:
            self.connection.close()
            self.logger.info("Closing connection to scale.")
        else:
            self.logger.info("Emulating close_connection scale.")

    def loop(self):
        self.logger.info("Start measuring with scale.")
       
        while self.run:
            
            if self.emulate:
                new_value = 10.0 + uniform(0.0, 0.2)
                self.add_new_value(new_value)
                self.timestamp = datetime.now()
            else:
                new_value = self.read_value_from_scale()
                
                if new_value is not None:
                    print("reached loop, new value not None")
                    self.add_new_value(new_value)
                    self.timestamp = datetime.now()
                else:
                    print("reached loop with new value = None")
            
            #deque scale history
            self.scale_history.appendleft(self.timestamp)
            self.scale_history.appendleft(new_value)
            
            sleep(5)

        self.logger.info("Stopped measuring with scale.")

    def start_measurement_thread(self):
        #self.publish = True
        self.run = True

        if self.thread.is_alive():
            self.logger.info("Already measuring.")
            return
        else:
            self.thread = Thread(target = self.loop)
            self.thread.start()
            self.threads.append(self.thread)
            #self.logger.info("Starting thread: " + self.thread.getName())
                    
    # diagnostics
    def print_diagnostics(self):
        print(self.threads)
        print(self.connection)
        print(self.connection.is_open)
        #print("Thread alive: " + str(self.thread.is_alive()))
        print("self.run = " + str(self.run))
        print(self.scale_history)
        print(self.flow_history)
       
    def stop_measurement_thread(self):
        self.run = False
        self.thread.join()
        #self.logger.info("Exiting Main Thread, Thread alive: " + str(self.thread.is_alive()))
        self.threads.remove(self.thread)

    # def toggle_publishing(self):
    #     if self.publish:
    #         self.publish = False
    #         self.logger.info("Still measuring, stopped publishing scale values via MQTT.")
    #         return
            
    #     self.publish = True
    #     self.logger.info("Publishing scale values via MQTT.")

    def read_value_from_scale(self):
        if self.connection is not None and self.connection.is_open:

            line = self.connection.readline()
            print("line: " + str(line))
            splitted_line = line.split()
            print("splitted_line: " + str(splitted_line))
            #del splitted_line[0]
            #print("splitted_line formatted: " + str(splitted_line))
            #print("splitted_line_formatted: " + splitted_line_formatted)
            self.logger.info("Measured {}".format(line))
            
            #print(len(splitted_line))
            if len(splitted_line) == 3:
                splitted_line_formatted = splitted_line[:2]
                #splitted_line_formatted = "".join(splitted_line[:2])
                print("splitted_line_formatted: " + str(splitted_line_formatted))
                new_value = str(splitted_line_formatted)
                print("new value, len == 3: " + str(new_value))
                return new_value
                
        else:
            print(self.connection.is_open)
            print(self.connection)
            self.open_connection()
            self.logger.info("Initialising connection to scale. Please retry.")

    def add_new_value(self, new_value):

        #calculate volume flow
        if len(self.scale_history) > 2:
            #dictionary: value, timestamp
            delta = self.scale_history[0] - self.scale_history[2]
            delta_weight = abs(delta)

            duration = self.scale_history[1] - self.scale_history[3]
            abs_duration = abs(duration)
            delta_time = abs_duration.total_seconds()
            
            weight_per_time = delta_weight / delta_time

            # density of water at normal pressure:
            # 10°C: 0.999702
            # 15°C: 0.999103
            # 20°C: 0.998207
            
            # weight_per_time divided by density gives volume flow
            volume_flow = round(weight_per_time / 0.999103, 10)
            
            self.flow_history.appendleft(volume_flow)
            
        # publish via mqtt
        # new_value = weight measured by scale
        # volume_flow = calculated volume flow 
        try:
            mqttmsg = StatusMessage("scale", new_value, "Kg", volume_flow, "L/s")
        except:
            mqttmsg = StatusMessage("scale", new_value, "Kg", None, None)
            

        if self.mqtt.connection_test():
            self.mqtt.publish_message(mqttmsg)

        if len(self.last_values) == 10:
            # calculate square mean error
            diffs = 0
            for value in list(islice(self.last_values, 0, 9)):
                diffs += abs(value - new_value)

            mean_diff = diffs / len(self.last_values)

            if mean_diff < 0.1:
                self.stable = True
                self.state = States.RUNNING
                return

        self.stable = False
        self.state = States.PAUSE

    def get_stable_value(self):
        if self.stable:
            return self.last_values[-1]
        else:
            self.logger.warning("No stable value. Scale varies until now.")
            return 0
