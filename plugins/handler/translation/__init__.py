import re
import difflib
import os.path

from HALlingual import translate, detect_lang
from HALapi import HALcannotHandle, clean_string

langmap = {'french': 'fr', 'german': 'de', 'english': 'en',
           'romanian': 'ro', 'chinese': 'zh', 'russian': 'ru',
           'spanish': 'es', 'portuguese': 'pt', 'italian': 'it',
           'dutch': 'nl'}
knownlang = langmap.keys()+langmap.values()
resayin = re.compile(r'Say (.+) in (.+)', re.I)

def trans(text, ilang, olang):
    ilang = ilang.lower()
    olang = olang.lower()
    ilang = clean_string(ilang, 'abcdefghijklmnopqrstuvwxyz')
    olang = clean_string(olang, 'abcdefghijklmnopqrstuvwxyz')
    ilang = langmap.get(ilang, ilang)
    olang = langmap.get(olang, olang)
    if ilang not in knownlang or olang not in knownlang:
        return "I don't know."
    out = translate(text, ilang, olang).capitalize().strip()
    if out and out[-1] not in '?!:,':
        out += '.'
    return out

def detect(m):
    text = m.group(1)
    ret = detect_lang(text)
    if ret is None:
        ret = 'en' # Default
    return ret

def check(input):
    return True

def answer(input):
    res = resayin.search(input)
    if res is not None:
        return trans(res.group(1), 'en', res.group(2))
    raise HALcannotHandle
