from skyfield.api import load

eph = load('de421.bsp')

class Planet:
    def __init__(self, name, eph_key):
        self.name = name
        self.body = eph[eph_key]

    def get_position(self, ts, date):
        astrometric = eph['earth'].at(date).observe(self.body).apparent()
        ra, dec, distance = astrometric.radec()
        return {
            'planet': self.name,
            'distance_au': distance.au,    #Distance from Earth in astronomical units (1 AU ≈ 149.6 million km).
            'right_ascension': ra,   #celestial longitude 
            'declination': dec  #celestial latitude
        }
   

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
