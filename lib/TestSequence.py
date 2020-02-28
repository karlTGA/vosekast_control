import logging
import threading
import time
import asyncio
import csv
#from lib.EnumStates import States

from lib.Log import LOGGER

from lib.utils.Msg import StatusMessage
from datetime import datetime


class TestSequence():
    # TestSequence states
    UNKNOWN = -1
    WAITING = 0
    MEASURING = 1
    PAUSED = 0.5
    STOPPED = 3

    def __init__(
        self,
        vosekast
    ):

        super().__init__()
        self.logger = logging.getLogger(LOGGER)
        self.vosekast = vosekast
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
            self.state = self.MEASURING
            self.vosekast.state = "PREPARING MEASUREMENT"

            # check if already running
            if self.scale.is_running != True:
                self.scale.open_connection()
                self.scale.start_measurement_thread()
                self.logger.info("Initialising scale connection & measurement thread. Please wait.")
                await asyncio.sleep(2)
            else:
                self.logger.debug("Scale running, continuing.")

            # set fill to True
            self.vosekast.constant_tank.start_fill

            #todo if already full
            
            #await constant_tank full
            #if self.vosekast.state == self.vosekast.INITED:
            await self.vosekast.constant_tank.fill()

            # check
            if not self.vosekast.ready_to_measure():
                self.logger.debug("Vosekast not ready to measure.")
                self.scale.print_diagnostics()
                return

            # create csv file
            self.vosekast.create_file()
            self.logger.info("Created csv file.")
            
            # turn on measuring pump, start measuring
            await self.start_measuring()

            self.vosekast.state = "MEASURING"

            #write to file
            await self.write_loop()
        
        #TankFillingTimeout
        except:
            self.logger.error("Error, aborting test sequence.")
            
            await self.stop_sequence()
            self.vosekast.constant_tank.stop_fill   
            self.vosekast.state = "RUNNING"         

    #todo fix drain

    async def write_loop(self):
        
        try:
            #null scale
            if abs(self.scale.scale_history[0]) < 0.15:
                scale_nulled = self.scale.scale_history[0]
            else:
                scale_nulled = 0

            while self.state == self.MEASURING and not self.vosekast.measuring_tank.is_filled:
                #get flow average
                flow_average = self.scale.flow_average()
                scale_actual = round(self.scale.scale_history[0] - scale_nulled, 5)
                #write values to csv file
                with open('sequence_values.csv', 'a', newline='') as file:
                    writer = csv.writer(file, delimiter=',',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
                    writer.writerow([self.scale.scale_history[1], scale_actual, self.scale.flow_history[0], flow_average])
                #todo dictionary als Datenspeicher
                self.logger.debug(str(scale_actual) +" kg, flow rate (average) "+ str(flow_average)+ " L/s")
                await asyncio.sleep(1)

            
            #todo sqlite
            
            #interrupt if measuring_tank full
            if self.vosekast.measuring_tank.is_filled:
                self.vosekast.measuring_tank_switch.close()
                self.vosekast.measuring_tank.drain_tank()
                self.logger.debug("Draining measuring tank, opening Measuring Tank bypass.")
        
        except:
            self.logger.warning("Write loop killed, stopping sequence.")
            await self.stop_sequence()
    
    async def start_measuring(self):
        try:
            self.vosekast.measuring_tank.prepare_to_fill()
            self.vosekast.measuring_tank_switch.close()
            self.vosekast.pump_measuring_tank.start()
            self.logger.debug("Measuring Pump spin up. Please wait.")

            await asyncio.sleep(5)

                                 
            self.vosekast.measuring_tank_switch.open()
            self.logger.debug("Measuring started.")
            
        except:
            self.logger.debug("Measuring aborted.")
            self.vosekast.pump_measuring_tank.stop()
            self.vosekast.state = "RUNNING"

    async def stop_sequence(self):
        self.state = self.STOPPED
        self.logger.debug('Stopped test sequence')
        self.vosekast.state = "RUNNING"

        # todo kill start_measurement
        
        self.vosekast.clean()
        
    def pause_sequence(self):
        self.state = self.PAUSED

        # set fill countdown to False
        for tank in self.vosekast.tanks:
            tank.stop_fill

        self.vosekast.measuring_tank_switch.close()
        self.vosekast.state = "RUNNING"
        self.logger.info("Paused. Measuring Tank bypass open.")

    async def continue_sequence(self):
        self.state = self.MEASURING

        # set fill countdown to True
        for tank in self.vosekast.tanks:
            tank.start_fill

        self.vosekast.measuring_tank_switch.open()
        self.vosekast.state = "MEASURING"
        self.logger.info("Continuing. Measuring Tank is being filled.")
        await self.write_loop()