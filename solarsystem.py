# planet_engine.py
from planet import Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune
from skyfield.api import load

class PlanetEngine:
    def __init__(self):
        self.ts = load.timescale()
        self.planets = {
            'Sun': None,    # optional: can be added later
            'Moon': None,   # optional
            'Mercury': Mercury(),
            'Venus': Venus(),
            'Mars': Mars(),
            'Jupiter': Jupiter(),
            'Saturn': Saturn(),
            'Uranus': Uranus(),
            'Neptune': Neptune()
        }

    def body_position(self, body_name, observer_latlon=(0,0), when=None):
        """
        Returns az, alt, RA, Dec, distance for GUI
        """
        if when is None:
            when = self.ts.utc_now()
        ts = self.ts
        date = ts.utc(when.year, when.month, when.day, when.hour, when.minute, when.second)

        planet = self.planets.get(body_name)
        if planet is None:
            raise ValueError(f"Body {body_name} not available")
        return planet.body_position(observer_latlon, ts, date)
