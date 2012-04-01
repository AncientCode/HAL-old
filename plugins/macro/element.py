import re
import sqlite3
import os.path
import HALapi

db = sqlite3.connect(os.path.join(HALapi.datadir, 'element.db'))
c = db.cursor()

iupac_temp_name = {
    '0': 'nil',
    '1': 'un',
    '2': 'bi',
    '3': 'tri',
    '4': 'quad',
    '5': 'pent',
    '6': 'hex',
    '7': 'sept',
    '8': 'oct',
    '9': 'en',
}

def is_num(str):
    try:
        int(str)
    except ValueError:
        return False
    else:
        return True

clean_num_ = ['st', 'nd', 'rd', 'th']
def clean_num(str):
    for i in clean_num_:
        str = str.replace(i, '')
    return str

def get_element_name_from_num(match):
    number_ = match.group(1)
    number = ''
    for i in number_:
        if is_num(i):
            number += i
    data = c.execute('SELECT name FROM elements WHERE z=?', (int(number),)).fetchall()
    if data:
        return data[0][0]
    name = ''
    for i in number:
        name += iupac_temp_name[i]
    return name+'ium'

def get_atomic_weight(match):
    words = match.group(1).split()
    filtered = []
    for word in words: 
        if c.execute('select * from elements where name like ?', (word,)).fetchall():
            filtered.append(word)
            break
        if is_num(clean_num(word)):
            filtered.append(clean_num(word))
            break
    if not filtered:
        return 'unknown'
    got = filtered[0]
    if is_num(got):
        res = c.execute('select weight from elements where z = ?', (int(got),)).fetchall()
        if not res:
            return 'unknown'
        return res[0][0]
    else:
        res = c.execute('select weight from elements where name like ?', (got,)).fetchall()
        if not res:
            return 'unknown'
        return res[0][0]
    
extended = {
    re.compile('\$ENAMEFNUM<(.*?)>\$'): get_element_name_from_num,
    re.compile('\$EWEIGHT<(.*?)>\$'): get_atomic_weight,
}
