from urllib import urlencode

# Module Level Constants
API_QUERY_CITY_DATA  = 'http://query.yahooapis.com/v1/public/yql'
API_YAHOO_WEATHER    = 'http://xml.weather.yahoo.com/forecastrss'
API_YAHOO_WEATHER_NS = 'http://xml.weather.yahoo.com/ns/rss/1.0'

def build_url(url, query):
    if isinstance(query, dict):
        query = urlencode(query)
    return '{url}?{args}'.format(url=url, args=query)
