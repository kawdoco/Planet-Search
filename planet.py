from skyfield.api import load, utc

eph = load('de421.bsp')

class Planet:
    def __init__(self, name, eph_key):
        self.name = name
        self.body = eph[eph_key]

    def body_position(self, observer_latlon=(0,0), ts=None, date=None):
        """
        Returns azimuth, altitude, RA, Dec, distance in AU
        """
        from skyfield.api import Topos
        if ts is None or date is None:
            raise ValueError("Time scale and date required")

        lat, lon = observer_latlon
        observer = eph['earth'] + Topos(latitude_degrees=lat, longitude_degrees=lon)
        astrom = observer.at(date).observe(self.body)
        ra, dec, distance = astrom.radec()
        alt, az, _ = astrom.apparent().altaz()
        return {
            'az_deg': az.degrees,
            'alt_deg': alt.degrees,
            'ra_hours': ra.hours,
            'dec_deg': dec.degrees,
            'distance_au': distance.au,
            'name': self.name
        }

# Planet subclasses
class Mercury(Planet):
    def __init__(self):
        super().__init__('Mercury', 'MERCURY BARYCENTER')

class Venus(Planet):
    def __init__(self):
        super().__init__('Venus', 'VENUS BARYCENTER')

class Mars(Planet):
    def __init__(self):
        super().__init__('Mars', 'MARS BARYCENTER')

class Jupiter(Planet):
    def __init__(self):
        super().__init__('Jupiter', 'JUPITER BARYCENTER')

class Saturn(Planet):
    def __init__(self):
        super().__init__('Saturn', 'SATURN BARYCENTER')

class Uranus(Planet):
    def __init__(self):
        super().__init__('Uranus', 'URANUS BARYCENTER')

class Neptune(Planet):
    def __init__(self):
        super().__init__('Neptune', 'NEPTUNE BARYCENTER')
