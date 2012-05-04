#encoding: utf-8
import urllib2
from urllib import urlencode, quote_plus
import json

__all__ = ['translate', 'detect_lang']

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

def translate(text, src, to='en'):
    data = dict(wl_srclang=wllang(src), wl_trglang=wllang(to), wl_text=text)
    data = urllib2.urlopen('http://www.worldlingo.com/S3704.3/texttranslate', urlencode(data)).read()
    if '<h1>An error occurred.</h1>' in data:
        return text
    return data.decode('utf-8')

def detect_lang(text, default='en'):
    data = dict(q=text, key='6305893b26c59ee77cab7ee0e0b787ea')
    data = json.load(urllib2.urlopen('http://ws.detectlanguage.com/0.2/detect', urlencode(data)))
    try:
        data = data['data']['detections'][0]['language']
        return data if data in langmap else default
    except (KeyError, IndexError):
        return None
    except urllib2.HTTPError:
        return default

if __name__ == '__main__':
    import codecs, sys
    sys.stdout = codecs.getwriter('mbcs')(sys.stdout, 'replace')
    text = 'A mathematical constant is a special number, usually a real number, that is "significantly interesting in some way". Constants arise in many different areas of mathematics, with constants such as e and pi occurring in such diverse contexts as geometry, number theory and calculus.'
    print 'Sample Text:', text
    lang = detect_lang(text)
    print 'Detect Lang:', lang
    tran = translate(text, lang, 'zh')
    print 'Chinese Translation:', translate(text, lang, 'zh')
    print 'Translating back:', translate(text, 'zh', lang)
