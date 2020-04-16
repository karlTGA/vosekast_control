import sqlite3
from sqlite3 import Error
import logging
import traceback
from vosekast_control.Log import LOGGER


class DBConnector:
    def __init__(self):
        self._db_connection = None
        self.logger = logging.getLogger(LOGGER)

    # cursor unnecessary according to https://docs.python.org/3/library/sqlite3.html#using-shortcut-methods
    def connect(self):
        try:
            self._db_connection = sqlite3.connect("run_values.db")
            self.cursor = self._db_connection.cursor()
            self.logger.info("Established DB connection.")
        except Error as e:
            self.logger.warning(e)
        except Exception:
            self.logger.info("Failed to establish DB connection.")
            traceback.print_exc()
            # raise

        self._db_connection.execute(
            """CREATE TABLE IF NOT EXISTS run_values (
            timestamp integer,
            scale_value real,
            flow_current real,
            flow_average real,
            pump_constant_tank_state real,
            pump_measuring_tank_state real,
            measuring_drain_valve_state text,
            measuring_tank_switch_state text,
            run_id text
            )"""
        )
        self._db_connection.commit()
        self.logger.info("DB created.")

    def insert_datapoint(self, data):
        try:
            # values = {
            #     'timestamp': 0000,
            #     'scale_current': 0000,
            #     'flow_current': 0000,
            #     'flow_average': 0000}

            # https://stackoverflow.com/questions/14108162/python-sqlite3-insert-into-table-valuedictionary-goes-here/16698310
            self._db_connection.execute(
                "INSERT INTO run_values (timestamp,scale_value,flow_current,flow_average,pump_constant_tank_state,pump_measuring_tank_state,measuring_drain_valve_state,measuring_tank_switch_state,run_id) VALUES (:timestamp, :scale_value, :flow_current, :flow_average, :pump_constant_tank_state, :pump_measuring_tank_state, :measuring_drain_valve_state, :measuring_tank_switch_state, :run_id);",
                data,
            )

            self._db_connection.commit()

        except Exception as e:
            self.logger.error(e)
            traceback.print_exc()
            # raise

    def read(self, data):
        # https://pynative.com/python-sqlite-select-from-table/
        data = data.get("data")
        self.cursor.execute("SELECT * FROM run_values WHERE data = ?", (data,))
        record = self.cursor.fetchall()
        return record

    # get sequence_id data from db
    def get_run_data(self, run_id: str):
        try:
            self.logger.debug(f"DB lookup for run_id: {run_id}")
            query = (run_id,)
            self.cursor.execute("SELECT * FROM run_values WHERE run_id = ?", query)
            return self.cursor.fetchall()

        except sqlite3.Error as e:
            self.logger.error("Failed to read data from sqlite table", e)

    def close(self):
        self._db_connection.close()
        self.logger.info("DB connection closed.")

    # workaround to show if connected
    # https://stackoverflow.com/questions/1981392/how-to-tell-if-python-sqlite-database-connection-or-cursor-is-closed
    # https://dba.stackexchange.com/questions/223267/in-sqlite-how-to-check-the-table-is-empty-or-not
    @property
    def isConnected(self):
        try:
            # should return 0 if empty
            self._db_connection.execute(
                "SELECT count(*) FROM (select 0 from sequence_values limit 1);"
            )
            return True
        except Error as e:
            self.logger.warning(e)
            return False
        except Exception:
            traceback.print_exc()
            # raise
            return False


DBConnection = DBConnector()
