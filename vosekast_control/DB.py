import sqlite3
from sqlite3 import Error
from datetime import datetime

class DBconnector():

    def __init__(self):
        self.dbconnect = sqlite3.connect('sequence_values.db')
        
    def db_connect(self):
        self.c = self.dbconnect.cursor()
        self.c.execute("""CREATE TABLE IF NOT EXISTS sequence_values (
            description text,
            timestamp real,
            scale_value real,
            flow_current real,
            flow_average_of_5 real
            )""")
        self.dbconnect.commit()

    def db_insertvalues(self, timestamp, scale_actual, flow_current, flow_average):
        # self.c.execute("INSERT INTO sequence_values VALUES (:description, :timestamp, :scale_value, :flow_current, :flow_average)", {
        #     'description': "description",
        #     'timestamp': self.scale.scale_history[1],
        #     'scale_value': scale_actual,
        #     'flow_current': self.scale.flow_history[0],
        #     'flow_average': flow_average
        #     })
        values = [('', 'timestamp', 'scale_actual', 'flow_current', 'flow_average'),]
        self.c.executemany("INSERT INTO sequence_values VALUES (:description, :timestamp, :scale_value, :flow_current, :flow_average)", values)

        self.dbconnect.commit()

    # todo def db_read(self):

    def db_close(self):
        self.dbconnect.close()

db_instance = DBconnector()

