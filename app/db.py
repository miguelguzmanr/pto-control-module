import sqlite3

DATABASE_NAME = 'log.db'

con = sqlite3.connect(DATABASE_NAME)
cur = con.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chassis_number TEXT,
    available_fuel REAL,
    vehicle_mass REAL,
    load_mass REAL,
    street_slope REAL,
    distance REAL,
    time REAL,
    max_rpm REAL,
    max_horsepower REAL,
    fuel_consumption REAL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
con.commit()
con.close()
