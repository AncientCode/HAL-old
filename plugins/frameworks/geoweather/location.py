import json
import urllib2

import api
import cache
from data import GeoLocation

__all__ = ['woeid', 'coord']

def get_info_on_location(location):
    params = {'q': 'select * from geo.places where text="{0}"'.format(location.replace('"', r'\"')),
              'format': 'json'}
    h = urllib2.urlopen(api.build_url(api.API_QUERY_CITY_DATA, params))
    page = h.read()
    h.close()
    try:
        data = json.loads(page)
    except ValueError:
        raise ValueError('Invalid Location!')
    try:
        return data['query']['results']['place'][0]
    except KeyError:
        pass
    try:
        return data['query']['results']['place']
    except KeyError:
        pass
    raise ValueError('Invalid Location!')

def woeid(location, use_cache=True):
    """
    Get the Yahoo! WOEID for a location.
    """
    if use_cache:
        woeid = cache.perma_get(location, 'woeid')
        if woeid is not None:
            return int(woeid)
    data = get_info_on_location(location)
    woeid = int(data['woeid'])
    if use_cache:
        cache.perma_set(location, woeid, 'woeid')
    return woeid

def coord(location, use_cache=True):
    """
    Get the latitude and longitude for a location.
    """
    if use_cache:
        coord = cache.perma_get(location, 'coord')
        if coord is not None:
            return GeoLocation(*map(float, coord.split(',')))
    data = get_info_on_location(location)
    latitude  = data['centroid']['latitude']
    longitude = data['centroid']['longitude']
    if use_cache:
        cache.perma_set(location, '{0},{1}'.format(latitude, longitude), 'coord')
    return GeoLocation(float(latitude), float(longitude))

def _test_module():
    cities = ['Toronto, Ontario, Canada', 'Mountain View',
              'Beijing, China', 'Bucharest, Romania']
    print 'Testing Yahoo! WOEID Fetcher:'
    def tester(loc, func):
        print '=== Location:', loc, '==='
        print 'With Cache:   ', func(loc, True)
        print 'Without Cache:', func(loc, False)
    test = lambda func: lambda x: tester(x, func)
    map(test(woeid), cities)
    print
    print 'Testing Latitude and Longitude:'
    map(test(coord), cities)

if __name__ == '__main__':
    _test_module()
