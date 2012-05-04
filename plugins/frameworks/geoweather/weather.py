import time
import urllib2
import datetime
from urllib import urlencode
from xml.dom import minidom

import api
from data import ForecastData, CurrentCondition, AngleData, WeatherData
import location as _location

__all__ = ['raw_yahoo_weather', 'get_all_data', 'direction_to_text']

def xml_get_ns_yahoo_tag(dom, ns, tag, attrs):
    """
    Parses the necessary tag and returns the dictionary with values
    
    Parameters:
    dom - DOM
    ns - namespace
    tag - necessary tag
    attrs - tuple of attributes

    Returns: a dictionary of elements 
    """
    element = dom.getElementsByTagNameNS(ns, tag)[0]
    return xml_get_attrs(element,attrs)


def xml_get_attrs(xml_element, attrs):
    """
    Returns the list of necessary attributes
    
    Parameters: 
    element: xml element
    attrs: tuple of attributes

    Return: a dictionary of elements
    """
    
    result = {}
    for attr in attrs:
        result[attr] = xml_element.getAttribute(attr)   
    return result


def raw_yahoo_weather(location_id, metric=True):
    """
    Fetches weather report from Yahoo!
    Note that this returns a lot more than weather.

    Parameters 
    location_id: The WOEID of the location, get_woeid() can retreive it.

    metric: type of units. True for metric and False for US units
    Note that choosing metric units changes all the weather units to metric, for example, wind speed will be reported as kilometers per hour and barometric pressure as millibars.
 
    Returns:
    weather_data: a dictionary of weather data that exists in XML feed. See  http://developer.yahoo.com/weather/#channel
    """
    params = dict(w=location_id, u='c' if metric else 'f')
    url = api.build_url(api.API_YAHOO_WEATHER, params)
    handler = urllib2.urlopen(url)
    dom = minidom.parse(handler)
    handler.close()
    
    try:
        weather_data = {}
        weather_data['title'] = dom.getElementsByTagName('title')[0].firstChild.data
        weather_data['link'] = dom.getElementsByTagName('link')[0].firstChild.data

        ns_data_structure = { 
            'location': ('city', 'region', 'country'),
            'units': ('temperature', 'distance', 'pressure', 'speed'),
            'wind': ('chill', 'direction', 'speed'),
            'atmosphere': ('humidity', 'visibility', 'pressure', 'rising'),
            'astronomy': ('sunrise', 'sunset'),
            'condition': ('text', 'code', 'temp', 'date')
        }       
        
        for (tag, attrs) in ns_data_structure.iteritems():
            weather_data[tag] = xml_get_ns_yahoo_tag(dom, api.API_YAHOO_WEATHER_NS, tag, attrs)

        weather_data['geo'] = {}
        weather_data['geo']['lat'] = dom.getElementsByTagName('geo:lat')[0].firstChild.data
        weather_data['geo']['long'] = dom.getElementsByTagName('geo:long')[0].firstChild.data

        weather_data['condition']['title'] = dom.getElementsByTagName('item')[0].getElementsByTagName('title')[0].firstChild.data
        weather_data['html_description'] = dom.getElementsByTagName('item')[0].getElementsByTagName('description')[0].firstChild.data
        
        forecasts = []
        for forecast in dom.getElementsByTagNameNS(api.API_YAHOO_WEATHER_NS, 'forecast'):
            forecasts.append(xml_get_attrs(forecast,('date', 'low', 'high', 'text', 'code')))
        weather_data['forecasts'] = forecasts
        
        dom.unlink()
    except IndexError:
        raise ValueError('Invalid Location')
    #weather_data['astronomy'] = dict([i, datetime.time(x) for i, x in weather_data['astronomy'].iteritems()])
    return weather_data

def parse_date(text):
    month = dict(jan=1, feb=2, mar=3, apr=4, may=5, jun=6, jul=7, aug=8, sep=9, oct=10, nov=11, dec=12)
    text = text.lower()
    for name, id in month.iteritems():
        text = text.replace(name, str(id))
    day, month, year = map(int, text.split())
    return datetime.date(year, month, day)

__all_data_cache = {}
__CACHE_EXPIRE = 60

def get_all_data(location, use_cache=True):
    if isinstance(location, basestring):
        location = _location.woeid(location)
    try:
        if not use_cache:
            raise KeyError
        expire, data = __all_data_cache[location]
        if expire+__CACHE_EXPIRE < time.time():
            raise KeyError
        return data
    except KeyError:
        pass
    raw = raw_yahoo_weather(location)
    current = raw['condition']
    forecasts = []
    for forecast in raw['forecasts']:
        high, low = int(forecast['high']), int(forecast['low'])
        data = ForecastData(parse_date(forecast['date']), high, low,
                            forecast['text'], xrange(low, high+1))
        forecasts.append(data)
    visib = raw['atmosphere']['visibility']
    humid = raw['atmosphere']['humidity']
    press = raw['atmosphere']['pressure']
    data = WeatherData(city=raw['location']['city'], region=raw['location']['region'],
                       country=raw['location']['country'],
                       humidity=float(humid)/100 if humid else None,
                       pressure=float(press)/10 if press else None,
                       visibility=float(visib)/100 if visib else None,
                       current=CurrentCondition(datetime.datetime.now(), int(current['temp']), current['text']),
                       forecasts=forecasts, windchill=raw['wind']['chill'],
                       winddirection=AngleData(deg=raw['wind']['direction']),
                       windspeed=float(raw['wind']['speed']))
    if use_cache:
        __all_data_cache[location] = (time.time(), data)
    return data


def direction_to_text(direction):
    wd = direction.deg
    if 348.75 <= wd < 360:
        return 'north'
    if 0 <= wd < 11.25:
        return 'north'
    if 11.25 <= wd < 33.75:
        return 'north-northeast'
    if 33.75 <= wd < 56.25:
        return 'northeast'
    if 56.25 <= wd < 78.75:
        return 'east-northeast'
    if 78.75 <= wd < 101.25:
        return 'east'
    if 101.25 <= wd < 123.75:
        return 'east-southeast'
    if 123.75 <= wd < 146.25:
        return 'southeast'
    if 146.25 <= wd < 168.75:
        return 'south-southeast'
    if 168.75 <= wd < 191.25:
        return 'south'
    if 191.25 <= wd < 213.75:
        return 'south-southwest'
    if 213.75 <= wd < 236.25:
        return 'southwest'
    if 236.25 <= wd < 258.75:
        return 'west-southwest'
    if 258.75 <= wd < 281.25:
        return 'west'
    if 281.25 <= wd < 303.75:
        return 'west-northwest'
    if 303.75 <= wd < 326.25:
        return 'northwest'
    if 326.25 <= wd < 348.75:
        return 'north-northwest'
    return 'north'


def _test_module():
    global __CACHE_EXPIRE
    from pprint import pprint
    from location import woeid
    print '== Testing Raw Weather =='
    print 'Retrieving raw weather data for Toronto, Canada'
    pprint(raw_yahoo_weather(woeid('Toronto, Canada')))
    print
    print 'Retrieving raw weather data for Brasov, Romania'
    pprint(raw_yahoo_weather(woeid('Brasov, Romania')))
    print
    print '== Testing Processed Weather =='
    city = 'Toronto, Canada'
    __CACHE_EXPIRE = 5
    print 'For:', 'Toronto, Canada'
    print '====== No Cache ======'
    pprint(get_all_data(city))
    print '====== With Cache ======'
    pprint(get_all_data(city))
    print '====== Expired Cache ======'
    time.sleep(6)
    pprint(get_all_data(city))
    print '====== Disabled Cache ======'
    pprint(get_all_data(city, False))

if __name__ == '__main__':
    _test_module()
