import re
import time
from getpass import getuser
import random

class HALmacro(object):
    redate = re.compile(r'\$DATE\$')
    retime = re.compile(r'\$TIME\$')
    redatetime = re.compile(r'\$DATETIME\$')
    reisotime  = re.compile(r'\$ISOTIME\$')
    readvdate  = re.compile(r'\$DATE\+(-?[0-9]+?)\$')
    readvtime  = re.compile(r'\$TIME\+(-?[0-9]+?)\$')
    readvdtime = re.compile(r'\$DATETIME\+(-?[0-9]+?)\$')
    readvitime = re.compile(r'\$ISOTIME\+(-?[0-9]+?)\$')
    rerandint  = re.compile(r'\$RANDINT@(-?[0-9]+?)~(-?[0-9]+?)\$')
    def __init__(self, user=None):
        self.basic = {
            '$USERNAME$'      : user if user is not None else getuser(),
            '$USER$'          : user if user is not None else getuser(),
            '$AGE$'           : str(random.randint(15, 40)),
            '$GENDER$'        : 'male',
            '$GENUS$'         : 'robot',
            '$SPECIES$'       : 'chatterbot',
            '$NAME$'          : 'HAL',
            '$MASTER$'        : 'Tudor and Guanzhong',
            '$BIRTHPLACE$'    : 'Toronto',
            '$FAVORITEFOOD$'  : 'electricity',
            '$FAVORITECOLOR$' : 'blue',
            '$BOTMASTER$'     : 'creator',
            '$WEBSITE$'       : 'dev.halbot.co.cc',
            '$RELIGION$'      : 'atheist',
        }
        self.extended = {
            self.redate:      lambda m: time.strftime('%B %d, %Y'),
            self.retime:      lambda m: time.strftime('%H:%M:%S'),
            self.redatetime:  lambda m: time.strftime('%H:%M:%S on %B %d, %Y'),
            self.reisotime:   lambda m: time.strftime('%Y-%m-%dT%H:%M:%S'),
            self.readvdate:   lambda m: time.strftime('%B %d, %Y', time.localtime(time.time()+int(m.group(1)))),
            self.readvtime:   lambda m: time.strftime('%H:%M:%S',  time.localtime(time.time()+int(m.group(1)))),
            self.readvdtime:  lambda m: time.strftime('%H:%M:%S on %B %d, %Y', time.localtime(time.time()+int(m.group(1)))),
            self.readvitime:  lambda m: time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(time.time()+int(m.group(1)))),
            self.rerandint:   lambda m: str(random.randint(int(m.group(1)), int(m.group(2)))),
        }
    def update_basic(self):
        pass
    def update_extended(self):
        pass
    def subst(self, input):
        if '$' in input:
            self.update_basic()
            for macro, replacement in self.basic.iteritems():
                input = input.replace(macro, replacement)
        if input[:2] == '@@':
            self.update_extended()
            input = input[2:]
            for regex, replacement in self.extended.iteritems():
                input = regex.sub(replacement, input)
        return input

if __name__ == '__main__':
    macro = HALmacro()
    while True:
        print macro.subst(raw_input('>>> '))
