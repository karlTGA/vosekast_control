import logging
import threading
import time
import asyncio
import csv

from lib.Log import LOGGER

from lib.EnumStates import States
from lib.utils.Msg import StatusMessage
from datetime import datetime


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
        self.valves = self.vosekast.valves
        self.tank = self.vosekast.tanks
        self.pumps = self.vosekast.pumps
        self.scale = self.vosekast.scale

        self.mqtt = self.vosekast.mqtt_client
        self.scale_value_start = []
        self.scale_value_stop = []

    def diagnostics(self):
        self.logger.info(self.state)
        self.logger.info(self.vosekast.measuring_drain_valve.is_closed)
        self.logger.info(self.vosekast.measuring_tank.is_filled)

    async def start_sequence(self):
        try:
            # check if already running
            if self.scale.is_running != True:
                self.scale.open_connection()
                self.scale.start_measurement_thread()

            self.logger.info("Initialising sequence.")
            
            #print("soon set state")
            # change state
            self.state = States.RUNNING
            self.tank.state = States.RUNNING
            self.change_state(self.state)
            print("state set, now await fill")

            # await constant_tank full
            await self.vosekast.constant_tank.fill()
            
            # check
            if not self.vosekast.ready_to_measure():
                self.logger.debug("Vosekast not ready to measure.")
                print("here")
                self.logger.debug("constant_tank_ready: " + str(constant_tank_ready))
                self.logger.debug("measuring_tank_ready: " + str(measuring_tank_ready))
                self.logger.debug("constant_pump_running: " + str(constant_pump_running))
                return

            # create csv file
            self.vosekast.create_file()
            self.logger.info("Created file.")
            print("here2")
            # todo turn on pump

            # loop
            while not self.vosekast.measuring_tank.is_filled and self.state == States.RUNNING:
                #write values to csv file
                with open('sequence_values.csv', 'a', newline='') as file:
                    writer = csv.writer(file, delimiter=',',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
                    writer.writerow([self.scale.scale_history[1], self.scale.scale_history[0]])
                #dictionary als Datenspeicher
                await asyncio.sleep(1)
            
            #todo jsondumps

            #interrupt if measuring_tank full
            if self.vosekast.measuring_tank.is_filled:
                self.stop_sequence()
        
        #TankFillingTimeout
        except:
            self.logger.error("TankFillingTimeout, aborting test sequence.")
            
            self.stop_sequence()
            self.logger.error("Stopped sequence.")
            


        

    def stop_sequence(self):
        self.state = States.STOPPED
        self.change_state(self.state)
        self.tank.state = States.STOPPED
        self.logger.debug('Stop sequence')
        self.vosekast.clean()

    def pause_sequence(self):
        self.state = States.PAUSE
        self.change_state(self.state)

    def continue_sequence(self):
        self.state = States.RUNNING
        self.change_state(self.state)

    def change_state(self, new_state):
        # publish via mqtt
        mqttmsg = StatusMessage("TestSequence State:", States(
            new_state).value, None, None, None)
        if self.mqtt.connection_test():
            self.mqtt.publish_message(mqttmsg)

    def send_new_data_point(self, x, y, index, legend):
        # self.send_data_point.emit(x, y, index, legend)

        # publish via mqtt
        mqttmsg = StatusMessage("TestSequence", str(
            x, y, index, legend), "data point", None, None)
        if self.mqtt.connection_test():
            self.mqtt.publish_message(mqttmsg)
