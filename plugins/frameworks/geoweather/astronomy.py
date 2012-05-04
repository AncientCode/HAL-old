"""GeoWeather framework's sunrise and sunset calculator"""

import ephem
import datetime

__all__ = ['sunrise', 'sunset']

class UTC(datetime.tzinfo):
    """UTC

    Optimized UTC implementation from pytz.
    """
    zone = "UTC"

    _utcoffset = datetime.timedelta(0)
    _dst = datetime.timedelta(0)
    _tzname = zone

    def fromutc(self, dt):
        if dt.tzinfo is None:
            return self.localize(dt)
        return super(utc.__class__, self).fromutc(dt)

    def utcoffset(self, dt):
        return datetime.timedelta(0)

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return datetime.timedelta(0)

    def __reduce__(self):
        return _UTC, ()

    def localize(self, dt, is_dst=False):
        '''Convert naive time to local time'''
        if dt.tzinfo is not None:
            raise ValueError('Not naive datetime (tzinfo is already set)')
        return dt.replace(tzinfo=self)

    def normalize(self, dt, is_dst=False):
        '''Correct the timezone information on the given datetime'''
        if dt.tzinfo is self:
            return dt
        if dt.tzinfo is None:
            raise ValueError('Naive time - no tzinfo set')
        return dt.astimezone(self)

    def __repr__(self):
        return "<UTC>"

    def __str__(self):
        return "UTC"

utc = UTC()

class StaticTzInfo(datetime.tzinfo):
    '''A timezone that has a constant offset from UTC
    from pytz

    These timezones are rare, as most locations have changed their
    offset at some point in their history
    '''
    _utcoffset = None
    _tzname = None
    zone = None

    def __init__(self, offset):
        self._utcoffset = datetime.timedelta(hours=offset)
        self._tzname = self.zone = 'UTF%+d'%offset
    def __str__(self):
        return self.zone
    def fromutc(self, dt):
        if dt.tzinfo is not None and dt.tzinfo is not self:
            raise ValueError('fromutc: dt.tzinfo is not self')
        return (dt + self._utcoffset).replace(tzinfo=self)
    def utcoffset(self, dt, is_dst=None):
        return self._utcoffset
    def dst(self, dt, is_dst=None):
        return _notime
    def tzname(self, dt, is_dst=None):
        return self._tzname
    def localize(self, dt, is_dst=False):
        if dt.tzinfo is not None:
            raise ValueError('Not naive datetime (tzinfo is already set)')
        return dt.replace(tzinfo=self)
    def normalize(self, dt, is_dst=False):
        if dt.tzinfo is self:
            return dt
        if dt.tzinfo is None:
            raise ValueError('Naive time - no tzinfo set')
        return dt.astimezone(self)
    def __repr__(self):
        return '<StaticTzInfo %r>' % (self.zone,)

def _calculate_time(date, coord, is_rise, utc_time, next):
    o = ephem.Observer()
    o.lat  = str(coord.latitude)
    o.long = str(coord.longitude)
    o.date = date
    sun = ephem.Sun(o)
    if next:
        event = o.next_rising if is_rise else o.next_setting
    else:
        event = o.previous_rising if is_rise else o.previous_setting
    return ephem.Date(event(sun, start=o.date) + int(utc_time)*ephem.hour).datetime().replace(tzinfo=StaticTzInfo(int(utc_time))).astimezone(utc)

def sunrise(coord, date=None):
    """coord should be a data.GeoLocation or a 2 element tuple: (lat, long)"""
    if date is None:
        date = datetime.date.today()
    zone = coord.longitude/15.0
    date = _calculate_time(date, coord, True, zone, True)
    return date, date.astimezone(StaticTzInfo(int(zone)))

def sunset(coord, date=None):
    """coord should be a data.GeoLocation or a 2 element tuple: (lat, long)"""
    if date is None:
        date = datetime.date.today()
    zone = coord.longitude/15.0
    date = _calculate_time(date, coord, False, zone, True)
    return date, date.astimezone(StaticTzInfo(int(zone)))

def _test_module():
    from location import coord
    cities = ['Toronto, Ontario, Canada', 'Mountain View',
              'Beijing, China', 'Bucharest, Romania']
    print 'Testing Sunrise and Sunset...'
    def tester(loc, time):
        print '=== Location:', loc, '==='
        coords = coord(loc)
        print 'Latitude:       ', coords.latitude
        print 'Longitude:      ', coords.longitude
        utc, local = sunrise(coords, time)
        print 'Sunrise (UTC):  ', utc
        print 'Sunrise (local):', local
        utc, local = sunset(coords, time)
        print 'Sunset (UTC):   ', utc
        print 'Sunset (local): ', local
    test = lambda time: lambda x: tester(x, time)
    print '===== Today ====='
    map(test(datetime.date.today()), cities)

if __name__ == '__main__':
    _test_module()
