import sqlite3
from sqlite3 import Error

from datetime import datetime

timestamp = datetime.now()

dbconnect = sqlite3.connect('values.db')

c = dbconnect.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS sequence_values (
             description text,
             timestamp real,
             scale_value real,
             flow_current real,
             flow_average_of_5 real
             )""")

c.execute("INSERT INTO sequence_values VALUES (:description, :timestamp, :scale_value, :flow_current, :flow_average)", {
    'description': "description", 
    'timestamp': timestamp, 
    'scale_value': timestamp,
    'flow_current': timestamp,
    'flow_average': timestamp
    })            

#c.execute("SELECT * FROM sequence_values WHERE description='description'")

#print(c.fetchone())

dbconnect.commit()

dbconnect.close()

# def create_connection(db_file):
#     """ create a database connection to the SQLite database
#         specified by db_file
#     :param db_file: database file
#     :return: Connection object or None
#     """
#     dbconnect = None
#     try:
#         dbconnect = sqlite3.connect(db_file)
#         return dbconnect
#     except Error as e:
#         print(e)
#     finally:
#         if dbconnect:
#             dbconnect.close()

# create_connection("values.db")