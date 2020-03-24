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

    def insertvalues(self, timestamp, scale_actual, flow_current, flow_average):
        try:
            # self.c.execute("INSERT INTO sequence_values VALUES (:description, :timestamp, :scale_value, :flow_current, :flow_average)", {
            #     'description': "description",
            #     'timestamp': self.scale.scale_history[1],
            #     'scale_value': scale_actual,
            #     'flow_current': self.scale.flow_history[0],
            #     'flow_average': flow_average
            #     })
            values = [('', 'timestamp', 'scale_actual', 'flow_current', 'flow_average'),]
            self._db_connection.executemany("INSERT INTO sequence_values VALUES (:description, :timestamp, :scale_value, :flow_current, :flow_average)", values)

            self._db_connection.commit()

        except Error as e:
            self.logger.warning(e)

    # todo def read(self):

    def close(self):
        self._db_connection.close()

    # todo 
    # https://stackoverflow.com/questions/1981392/how-to-tell-if-python-sqlite-database-connection-or-cursor-is-closed
    @property
    def isConnected(self):
        try:
            result = self._db_connection.execute("SELECT 1 FROM sequence_values LIMIT 1;")
            return True
        except ProgrammingError as e:
            self.logger.warning(e)
            return False

db_instance = DBconnector()

