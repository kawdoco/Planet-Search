import mysql.connector
from datetime import datetime
from skyfield.api import load, utc
from planet import Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune

# Map planet names to classes
planet_classes = {
    'mercury': Mercury,
    'venus': Venus,
    'mars': Mars,
    'jupiter': Jupiter,
    'saturn': Saturn,
    'uranus': Uranus,
    'neptune': Neptune
}

class SolarSystem:
    def __init__(self, db_config):
        self.ts = load.timescale()
        self.conn = mysql.connector.connect(**db_config)
        self.c = self.conn.cursor()

        # Create table if it doesn't exist
        self.c.execute('''
        CREATE TABLE IF NOT EXISTS planet_positions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            planet VARCHAR(50),
            date DATETIME,
            distance_au DOUBLE,
            right_ascension VARCHAR(50),
            declination VARCHAR(50)
        )
        ''')
        self.conn.commit()

    def calculate_position(self, planet_name, date_str):
        planet_class = planet_classes.get(planet_name.lower())
        if not planet_class:
            return None

        planet = planet_class()
        date = self.ts.utc(datetime.strptime(date_str, "%Y-%m-%d %H:%M").replace(tzinfo=utc))
        return planet.get_position(self.ts, date)

    def save_to_db(self, planet_data, date_str):
        # Convert RA/Dec to string
        ra_str = planet_data['right_ascension'].hstr()
        dec_str = planet_data['declination'].dstr()

        # Check if record already exists
        self.c.execute('''
            SELECT * FROM planet_positions
            WHERE planet = %s AND date = %s
        ''', (planet_data['planet'], date_str))

        if self.c.fetchone() is None:
            self.c.execute('''
                INSERT INTO planet_positions (planet, date, distance_au, right_ascension, declination)
                VALUES (%s, %s, %s, %s, %s)
            ''', (planet_data['planet'], date_str, planet_data['distance_au'], ra_str, dec_str))
            self.conn.commit()
            print(f"{planet_data['planet']} position saved to MySQL database successfully.")
        else:
            print(f"{planet_data['planet']} at {date_str} already exists in the database. Skipping insert.")

    def display(self, planet_data):
        print()
        print(f"{'Planet':<10} {'Distance(AU)':<15} {'Right Ascension':<20} {'Declination':<20}")
        print(f"{planet_data['planet']:<10} {planet_data['distance_au']:<15.6f} {planet_data['right_ascension'].hstr():<20} {planet_data['declination'].dstr():<20}")
        print()

    def close(self):
        self.conn.close()
