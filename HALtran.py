#encoding: utf-8 
import urllib2 
from urllib import urlencode, quote_plus 
import json 
import sys
import time
import random
import difflib

langmap = { 
    'el': 'EL', 
    'en': 'EN', 
    'it': 'IT', 
    'bg': 'LWA_BG', 
    'cs': 'LWA_CS', 
    'es': 'ES', 
    'ru': 'RU', 
    'nl': 'NL', 
    'pt': 'PT', 
    'zh': 'ZH_CN', 
    'tr': 'LWA_TR', 
    'th': 'LWA_TH', 
    'ro': 'LWA_RO', 
    'pl': 'LWA_PL', 
    'fr': 'FR', 
    'ps': 'LWA_PS', 
    'de': 'DE', 
    'da': 'LWA_DA', 
    'fa': 'LWA_FA', 
    'hi': 'LWA_HI', 
    'fi': 'LWA_FI', 
    'ha': 'LWA_HA', 
    'ja': 'JA', 
    'he': 'LWA_HE', 
    'sr': 'LWA_SR', 
    'no': 'LWA_NO', 
    'ko': 'KO', 
    'sv': 'SV', 
    'ur': 'LWA_UR', 
    'so': 'LWA_SO', 
    'hu': 'LWA_HU' 
} 
 
def wllang(id): 
    if id.lower() in langmap: 
        return langmap[id.lower()] 
    else: 
        return id.upper()
 
def translate(text, src, to): 
    data = dict(wl_srclang=wllang(src), wl_trglang=wllang(to), wl_text=text.encode('utf-8')) 
    data = urllib2.urlopen('http://www.worldlingo.com/S3704.3/texttranslate', urlencode(data)).read().decode('utf-8')
    if 'An error occurred.' in data:
        return None
    return data
 
def detect_lang(text): 
    data = dict(q=text, key='6305893b26c59ee77cab7ee0e0b787ea') 
    data = json.load(urllib2.urlopen('http://ws.detectlanguage.com/0.2/detect', urlencode(data))) 
    try: 
        data = data['data']['detections'][0]['language'] 
        return data 
    except KeyError: 
        print 'GotKeyError' 
        return None 
 
#langs = ['en', 'it', 'pt', 'fr', 'de', 'ro']
langs = ['en', 'fr']
def transform(text):
    lang = random.choice(langs)
    inter = output = text
    if lang != 'en':
        text_1 = translate(text, 'en', lang).strip()
        if text_1 is None:
            output = text
        else:
            text_2 = translate(text_1, lang, 'en').strip()
            if text_2 is None:
                output = text
            else:
                output = text_2
            inter = text_1
    if difflib.SequenceMatcher(a=text, b=output).ratio() < 0.7:
        output = text
    return lang, inter, output

if __name__ == '__main__':
    import codecs
    sys.stdout = codecs.getwriter('mbcs')(sys.stdout, 'replace')
    while True:
        input = raw_input('--> ').decode(sys.stdin.encoding)
        lang, inter, out = transform(input)
        print 'Language:', lang
        print 'Intermediate:', inter
        print 'Output:', out
