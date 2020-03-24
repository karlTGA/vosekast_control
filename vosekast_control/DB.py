import sqlite3
from sqlite3 import Error
from datetime import datetime

class DBconnector():

    def __init__(self):
        self._db_connection = None
        
    def connect(self):
        try:
            self._db_connection = sqlite3.connect('sequence_values.db')
        except Error as e:
            self.logger.warning(e)

        #cursor unnecessary according to https://docs.python.org/3/library/sqlite3.html#using-shortcut-methods
        #cursor = self._db_connection.cursor()
        self._db_connection.execute("""CREATE TABLE IF NOT EXISTS sequence_values (
            description text,
            timestamp real,
            scale_value real,
            flow_current real,
            flow_average_of_5 real
            )""")
        self._db_connection.commit()

    def insert_datapoint(self, values):
        try:
            # values = {
            #     'timestamp': 0000, 
            #     'scale_actual': 0000,
            #     'flow_current': 0000,
            #     'flow_average': 0000}
            self._db_connection.executemany("INSERT INTO sequence_values VALUES (:timestamp, :scale_value, :flow_current, :flow_average)", values)

            self._db_connection.commit()

        except Error as e:
            self.logger.warning(e)

    # todo def read(self):

    def close(self):
        self._db_connection.close()

    # todo 
    # https://stackoverflow.com/questions/1981392/how-to-tell-if-python-sqlite-database-connection-or-cursor-is-closed
    # https://dba.stackexchange.com/questions/223267/in-sqlite-how-to-check-the-table-is-empty-or-not
    @property
    def isConnected(self):
        try:
            #should return 0 if empty
            self._db_connection.execute("SELECT count(*) FROM (select 0 from sequence_values limit 1);")
            return True
        except ProgrammingError as e:
            self.logger.warning(e)
            return False

db_instance = DBconnector()

