import re
import socket
import urllib2
import os.path

import HALsharedData

def get_ip():
    try:
        return urllib2.urlopen('http://automation.whatismyip.com/n09230945.asp').read().strip()
    except urllib2.HTTPError:
        return socket.gethostbyname(socket.gethostname())

def get_location():
    page = urllib2.urlopen('http://www.tracemyip.org').read().replace('&nbsp;', '')
    recity = re.compile('<td valign="top" class="tID_01"><b>Hub City:</b>(.*?)<br>', re.S)
    recoun = re.compile('<td class="tID_01"><b>Country:</b>(.*?)</table>', re.S)
    reloc = re.compile('<td class="tID_01"><b>State:</b></td>(.*?)</tr>', re.S)
    reclean = re.compile('<.*?>') 
    city = reclean.sub('', recity.search(page).group(1).replace(' ', '')).strip()
    location = reclean.sub('', reloc.search(page).group(1).replace(' ', '')).strip()
    country = reclean.sub('', recoun.search(page).group(1).replace(' ', '')).strip()
    return city, location, country

city, location, country = get_location()
basic = {
    '$IP$'      : get_ip(),
    '$LOCATION$': '%s, %s, %s'%(city, location, country),
    '$CITY$'    : city,
    '$PROVINCE$': location,
    '$COUNTRY$' : country,
}

HALsharedData.location = '%s, %s, %s'%(city, location, country)
HALsharedData.city = city
HALsharedData.province = location
HALsharedData.country = country

halfiles = [os.path.join(os.path.dirname(__file__), 'iploc.hal')]
