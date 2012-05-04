import re
import os.path

import geoweather
import HALsharedData

currentconditions_fmt = "It's now {desc}, with a temperature of {temp} degrees Celcius in {loc}."
#currentconditions_fmt = "{wind}atmospheric pressure of {pres} kPa, {visib}and {wc}."
wind_fmt = "wind speed of {speed} km/h from {direction}, "
humid_fmt = 'Humidity of {:.0f}%, '
pres_fmt = 'atmospheric pressure of {} kPa, '

def currentconditions(match):
    location = match.group(1)
    if location is None:
        location = HALsharedData.location
    weather = geoweather.get_all_data(location)
    #location = ', '.join(filter(bool, (weather.city, weather.region, weather.country)))
    location = weather.city
    if weather.windspeed:
        wind = wind_fmt.format(speed=weather.windspeed,
                               direction=geoweather.direction_to_text(weather.winddirection))
    else:
        wind = 'no wind, '
    if weather.visibility is not None:
        visib = 'visibility of {dist} km, '.format(dist=weather.visibility)
    else:
        visib = ''
    if int(weather.windchill) != int(weather.current.temp):
        wc = 'wind chill of {temp} degrees Celcius'.format(temp=weather.windchill)
    else:
        wc = 'no wind chill'
    if weather.humidity is not None:
        humid = humid_fmt.format(weather.humidity*100)
    else:
        humid = ''
    if weather.pressure is not None:
        pres = pres_fmt.format(weather.pressure)
    else:
        pres = ''
    details = filter(bool, [wind, pres, visib, wc])
    if len(details) == 1:
        detail = details[0].rstrip(', ')+'.'
    else:
        detail = ''.join(details[:-1])+'and '+details[-1]+'.'
    detail = detail[0].upper()+detail[1:]
    return currentconditions_fmt.format(desc=weather.current.desc.lower(),
                                        temp=weather.current.temp,
                                        loc=location)+' '+detail

def forecast(match):
    day = match.group(1)
    location = match.group(2)
    if location is None:
        location = HALsharedData.location
    day_map = dict(today=0, tom=1)
    if day not in day_map:
        return "The far future is unpredictable."
    weather = geoweather.get_all_data(location)
    forecast = weather.forecasts[day_map[day]]
    if day == 'tom':
        day = 'tomorrow'
    desc = forecast.desc.lower()
    propernames = {
        'rain': 'It will rain',
        'isolated thunderstorms': 'There will be isolated thunderstorms',
    }
    desc = propernames.get(desc, desc)
    desc = desc.replace('pm', 'morning').replace('pm', 'afternoon').capitalize()
    return '{desc} {day}, with high of {high} degrees Celcius \
and low of {low} degrees Celcius in {loc}.'.format(desc=desc, day=day,
                                                   loc=weather.city,
                                                   high=forecast.high,
                                                   low=forecast.low)

extended = {
    re.compile(r'\$currentconditions(?:\(([^)]+)\))?\$'): currentconditions,
    re.compile(r'\$forecast\(([^(),]+)(?:\s*,\s*([^()]+))?\)\$'): forecast,
}

halfiles = [os.path.join(os.path.dirname(__file__), 'weather.hal')]
