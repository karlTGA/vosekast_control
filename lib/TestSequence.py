import logging
import threading
import time
import asyncio

from lib.Log import LOGGER

from lib.EnumStates import States
from lib.utils.Msg import StatusMessage


class TestSequence():
    def __init__(
        self,
        vosekast,
        default_state=States.READY
    ):

        super().__init__()
        self.logger = logging.getLogger(LOGGER)
        self.vosekast = vosekast
        self.state = default_state
        self.valves = vosekast.valve
        self.tank = vosekast.tank
        self.scale = vosekast.scale
        

        self.mqtt = self.vosekast.mqtt_client
        self.scale_value_start = []
        self.scale_value_stop = []

    def diagnostics(self):
        self.logger.info(self.state)

    async def start_sequence(self):
        #check if already running
        if not self.scale.stop_measurement_thread() and not self.scale.close_connection():
            self.scale.start_measurement_thread()
            self.scale.open_connection()

        self.logger.info("Initialising sequence.")
        
        #change state
        self.state = States.RUNNING
        self.change_state(self.state)

        #prepare measuring
        self.vosekast.prepare_measuring()
        #await base_tank full
        await self.tank.base_tank._on_full()
        #check
        self.vosekast.ready_to_measure()
        #start
        self.vosekast.start_measuring()
        #get scale value t0
        scale_value_start = self.scale.read_value_from_scale()

        #self.timer.start(500)

    def stop_sequence(self):
        scale_value_stop = self.scale.read_value_from_scale()

        self.state = States.STOPPED
        self.change_state(self.state)

        self.vosekast.clean()

    def pause_sequence(self):
        self.state = States.PAUSE
        self.change_state(self.state)

    def continue_sequence(self):
        self.state = States.RUNNING
        self.change_state(self.state)

    def change_state(self, new_state):
        # publish via mqtt
        mqttmsg = StatusMessage("TestSequence", States(new_state).value, None, None, None)
        if self.mqtt.connection_test():
            self.mqtt.publish_message(mqttmsg)

    def send_new_data_point(self, x, y, index, legend):
        # self.send_data_point.emit(x, y, index, legend)

        # publish via mqtt
        mqttmsg = StatusMessage("TestSequence", str(
            x, y, index, legend), "data point", None, None)
        if self.mqtt.connection_test():
            self.mqtt.publish_message(mqttmsg)