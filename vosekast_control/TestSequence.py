import logging
import threading
import time
import asyncio
import csv

from vosekast_control.Log import LOGGER

import sqlite3
from sqlite3 import Error
from datetime import datetime


class TestSequence():
    # TestSequence states
    UNKNOWN = "UNKNOWN"
    WAITING = "WAITING"
    MEASURING = "MEASURING"
    PAUSED = "PAUSED"
    STOPPED = "STOPPED"

    def __init__(
        self,
        vosekast,
        emulate=False,
    ):

        super().__init__()
        self.logger = logging.getLogger(LOGGER)
        self.vosekast = vosekast
        self.valves = self.vosekast.valves
        self.tank = self.vosekast.tanks
        self.pumps = self.vosekast.pumps
        self.scale = self.vosekast.scale
        self.emulate = emulate
        self.state = self.UNKNOWN
        self.mqtt = self.vosekast.mqtt_client
        self.scale_value_start = []
        self.scale_value_stop = []

    async def start_sequence(self):
        if not self.state == self.WAITING and not self.state == self.MEASURING:
            try:
                self.logger.info("Initialising sequence.")

                # change state
                self.state = self.WAITING
                
                # check if already running
                if self.scale.is_running != True:
                    self.scale.start()
                    self.logger.info(
                        "Initialising scale connection & measurement thread. Please wait.")
                    await asyncio.sleep(1)
                else:
                    self.logger.debug("Scale running, continuing.")

                # only fill if not already full
                if not self.vosekast.constant_tank.state == self.vosekast.constant_tank.FILLED:
                    self.vosekast.constant_tank.state = self.vosekast.constant_tank.IS_FILLING
                    # await constant_tank full
                    await self.vosekast.constant_tank.fill()
                else:
                    self.vosekast.prepare_measuring()

                # check ready_to_measure
                if not self.vosekast.ready_to_measure:
                    self.logger.debug("Vosekast not ready to measure.")
                    self.scale.print_diagnostics()
                    self.state = self.STOPPED
                    return
                
                # check if state has been changed
                elif self.state == self.STOPPED or self.state == self.PAUSED:
                    return

                # turn on measuring pump, start measuring
                await self.start_measuring()

                self.vosekast.state = self.vosekast.MEASURING
                self.state = self.MEASURING

                # write to file
                await self.write_loop()

            # TankFillingTimeout
            except:
                self.logger.error("Error, aborting test sequence.")

                await self.stop_sequence()
                self.vosekast.constant_tank.state = self.vosekast.constant_tank.STOPPED
                self.vosekast.state = self.vosekast.RUNNING
        else:
            self.logger.info("Already measuring.")

    async def write_loop(self):
        try:
            time_sequence_t0 = datetime.now()
            delta_time_sequence = 0
            # null scale
            if abs(self.scale.scale_history[0]) < 0.15:
                scale_nulled = self.scale.scale_history[0]
            else:
                scale_nulled = 0

            while self.state == self.MEASURING and not self.vosekast.measuring_tank.is_filled:
                # get flow average
                flow_average = self.scale.flow_average()

                if self.emulate and delta_time_sequence >= 30:
                    self.vosekast.measuring_tank.state = self.vosekast.measuring_tank.FILLED
                if self.emulate:
                    # timeout
                    time_sequence_t1 = datetime.now()
                    time_sequence_passed = time_sequence_t1 - time_sequence_t0
                    delta_time_sequence = time_sequence_passed.total_seconds()

                    scale_actual = round(self.scale.scale_history[0], 5)
                else:
                    scale_actual = round(
                    self.scale.scale_history[0] - scale_nulled, 5)

                # todo move the db init in a class or a singleton
                #db
                dbconnect = sqlite3.connect('sequence_values.db')
                c = dbconnect.cursor()
                c.execute("""CREATE TABLE IF NOT EXISTS sequence_values (
                    description text,
                    timestamp real,
                    scale_value real,
                    flow_current real,
                    flow_average_of_5 real
                    )""")

                dbconnect.commit()

                try:
                    c.execute("INSERT INTO sequence_values VALUES (:description, :timestamp, :scale_value, :flow_current, :flow_average)", {
                        'description': "description",
                        'timestamp': self.scale.scale_history[1],
                        'scale_value': scale_actual,
                        'flow_current': self.scale.flow_history[0],
                        'flow_average': flow_average
                    })

                    dbconnect.commit()

                except Error as e:
                    self.logger.warning(e)

                except:
                    self.logger.warning("Error writing to db.")
                    dbconnect.close()

                self.logger.debug(
                    str(scale_actual) + " kg, flow rate (average) " + str(flow_average) + " L/s")
                await asyncio.sleep(1)

            dbconnect.close()

            # todo sqlite

            # interrupt if measuring_tank full
            if self.vosekast.measuring_tank.is_filled:
                self.vosekast.measuring_tank_switch.close()
                self.vosekast.measuring_tank.drain_tank()
                self.state = self.STOPPED
                self.logger.debug(
                    "Draining measuring tank, opening Measuring Tank bypass.")

        except:
            self.logger.warning("Write loop killed, stopping sequence.")
            dbconnect.close()
            await self.stop_sequence()

    async def start_measuring(self):
        try:
            self.vosekast.measuring_tank.prepare_to_fill()
            self.vosekast.measuring_tank_switch.close()
            self.vosekast.pump_measuring_tank.start()
            self.logger.debug("Measuring Pump spin up. Please wait.")

            await asyncio.sleep(3)

            self.vosekast.measuring_tank_switch.open()
            self.logger.debug("Measuring started.")

        except:
            self.logger.debug("Measuring aborted.")
            self.vosekast.pump_measuring_tank.stop()
            self.vosekast.state = "RUNNING"

    async def stop_sequence(self):
        if self.state == self.MEASURING or self.state == self.PAUSED or self.state == self.WAITING:
            self.state = self.STOPPED
            self.vosekast.measuring_tank_switch.close()
            self.logger.debug('Stopped test sequence')
            self.vosekast.state = self.vosekast.RUNNING

            # todo kill start_measurement

            self.vosekast.clean()
        else:
            self.logger.info("Sequence has not yet been started.")

    def pause_sequence(self):
        if self.state == self.MEASURING:
            self.state = self.PAUSED

            # set fill countdown to False
            self.vosekast.constant_tank.state = self.vosekast.constant_tank.PAUSED

            # switch to measuring_tank bypass
            self.vosekast.measuring_tank_switch.close()
            
            self.logger.info("Paused. Measuring Tank bypass open.")
        
        # if constant_tank has not been filled yet
        elif self.state == self.WAITING and self.vosekast.PREPARING_MEASUREMENT:
            self.state = self.STOPPED
            self.vosekast.state = self.vosekast.RUNNING
            self.logger.info("Measuring has not yet started, continuing to fill constant_tank.")
        elif self.state == self.PAUSED or self.state == self.STOPPED:
            self.logger.info("Sequence already paused.")
        else:
            self.logger.info("Sequence has not yet been started.")

    async def continue_sequence(self):
        if self.state == self.PAUSED:
            self.state = self.MEASURING

            # set fill countdown to True
            self.vosekast.constant_tank.state = self.vosekast.constant_tank.IS_FILLING

            self.vosekast.measuring_tank_switch.open()
            self.logger.info("Continuing. Measuring Tank is being filled.")
            await self.write_loop()
        elif self.state == self.WAITING or self.state == self.MEASURING:
            self.logger.info("Sequence has not been paused.")
        else:
            self.logger.info("Sequence has not yet been started.")

