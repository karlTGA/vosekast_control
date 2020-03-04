import sqlite3

dbconnect = sqlite3.connect('values.db')

c = dbconnect.cursor()


c.execute(
    description text,
    values real
    )

dbconnect.commit()

dbconnect.close()