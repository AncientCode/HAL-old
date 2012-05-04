import math
from operator import itemgetter
from collections import OrderedDict, namedtuple

__all__ = ['GeoLocation', 'AngleData', 'ForecastData', 'CurrentCondition', 'WeatherData']

class GeoLocation(tuple):
    """Represents a location on Earth"""
    __slots__ = ()
    _fields = ('latitude', 'longitude')
    
    def __new__(_cls, latitude, longitude):
        """Create new instance of GeoLocation(latitude, longitude)"""
        return tuple.__new__(_cls, (latitude, longitude))
    
    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        """Make a new GeoLocation object from a sequence or iterable"""
        result = new(cls, iterable)
        if len(result) != 2:
            raise TypeError('Expected 2 arguments, got %d' % len(result))
        return result
    
    def __repr__(self):
        """Return a nicely formatted representation string"""
        return 'GeoLocation(latitude=%r, longitude=%r)' % self
    
    def _asdict(self):
        """Return a new OrderedDict which maps field names to their values"""
        return OrderedDict(zip(self._fields, self))
    
    __dict__ = property(_asdict)
    
    def _replace(_self, **kwds):
        """Return a new GeoLocation object replacing specified fields with new values"""
        result = _self._make(map(kwds.pop, ('latitude', 'longitude'), _self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result
    
    def __getnewargs__(self):
        """Return self as a plain tuple.  Used by copy and pickle."""
        return tuple(self)
    
    latitude = property(itemgetter(0), doc='Latitude of the location')
    longitude = property(itemgetter(1), doc='Longitude of the location')

class AngleData(object):
    def __init__(self, deg=None, rad=None):
        if rad is None:
            rad = math.radians(float(deg))
        self._rad = float(rad)
    
    @property
    def deg(self):
        """Get result in degrees"""
        return math.degrees(self._rad)
    
    @deg.setter
    def deg(self, value):
        self._rad = math.radians(value)
    
    @property
    def rad(self):
        """Get result in radians"""
        return self._rad
    
    @rad.setter
    def rad(self, value):
        self._rad = value
    
    def __str__(self):
        return '%f radians'%self._rad
    
    def __repr__(self):
        return 'AngleData(deg=%s, rad=%s)'%(repr(self.deg), repr(self.rad))

ForecastData = namedtuple('ForecastData', ['date', 'high', 'low', 'desc', 'range'])
CurrentCondition = namedtuple('CurrentCondition', ['datetime', 'temp', 'desc'])
WeatherData = namedtuple('WeatherData', ['city', 'region', 'country',
                                         'humidity', 'pressure', 'visibility',
                                         'current', 'forecasts', 'windchill',
                                         'winddirection', 'windspeed'])
