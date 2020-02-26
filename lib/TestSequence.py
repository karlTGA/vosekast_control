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

    async def start_sequence(self):
        try:
            self.logger.info("Initialising sequence.")

            # change state
            self.state = States.RUNNING
            self.change_state(self.state)

            # check if already running
            if self.scale.is_running != True:
                self.scale.open_connection()
                self.scale.start_measurement_thread()
                self.logger.info("Initialising connection, measurement thread. Please wait.")
                await asyncio.sleep(2)
            else:
                self.logger.debug("Scale running, continuing.")

            # set fill to True
            self.vosekast.constant_tank.start_fill
            # await constant_tank full
            await self.vosekast.constant_tank.fill()
            
            # check
            if not self.vosekast.ready_to_measure():
                self.logger.debug("Vosekast not ready to measure.")
                self.scale.print_diagnostics()
                return

            # create csv file
            self.vosekast.create_file()
            self.logger.info("Created file.")
            
            # turn on measuring pump, start measuring
            self.vosekast.measuring_tank.start_measuring()
            await self.write_loop()
        
        #TankFillingTimeout
        except:
            self.logger.error("Error, aborting test sequence.")
            
            await self.stop_sequence()
            self.vosekast.constant_tank.stop_fill            

    async def write_loop(self):
        try:
            # loop
            while self.state == States.RUNNING and not self.vosekast.measuring_tank.is_filled:
                #write values to csv file
                with open('sequence_values.csv', 'a', newline='') as file:
                    writer = csv.writer(file, delimiter=',',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
                    writer.writerow([self.scale.scale_history[1], self.scale.scale_history[0], self.scale.flow_history[0], self.scale.flow_average()])
                #todo dictionary als Datenspeicher
                #self.logger.debug("flow average: " + str(self.scale.flow_average()))                
                await asyncio.sleep(1)
                            
            #todo jsondumps
            self.logger.debug("loop testsequence ended")
            #interrupt if measuring_tank full
            if self.vosekast.measuring_tank.is_filled:
                self.logger.info("Measuring Tank full, stopping sequence.")
                await self.stop_sequence()
        
        except:
            self.logger.info("Write loop killed.")
            

    async def stop_sequence(self):
        self.state = States.STOPPED
        self.change_state(self.state)
        self.logger.debug('Stopped test sequence')

        # set fill to False
        for tank in self.vosekast.tanks:
            tank.stop_fill

        # todo kill start_measurement

        await self.vosekast.clean()

    async def pause_sequence(self):
        self.state = States.PAUSE
        self.change_state(self.state)
        self.vosekast.measuring_tank_switch.close()

    async def continue_sequence(self):
        self.state = States.RUNNING
        self.change_state(self.state)
        self.vosekast.measuring_tank_switch.open()
        await self.write_loop()

    def change_state(self, new_state):
        # publish via mqtt
        mqttmsg = StatusMessage("TestSequence State:", States(
            new_state).value, None, None, None)
        if self.mqtt.connection_test():
            self.mqtt.publish_message(mqttmsg)

    def send_new_data_point(self, x, y, index, legend):

        # publish via mqtt
        mqttmsg = StatusMessage("TestSequence", str(
            x, y, index, legend), "data point", None, None)
        if self.mqtt.connection_test():
            self.mqtt.publish_message(mqttmsg)
