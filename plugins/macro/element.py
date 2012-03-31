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

def get_element_name_from_num(match):
    number_ = match.group(1)
    number = ''
    for i in number_:
        if i in '0123456789':
            number += i
    data = c.execute('SELECT name FROM elements WHERE z=?', (int(number),)).fetchall()
    if data:
        return data[0][0]
    name = ''
    for i in number:
        name += iupac_temp_name[i]
    return name+'ium'

extended = {
    re.compile('\$ENAMEFNUM<(.*?)>\$'): get_element_name_from_num,
}
