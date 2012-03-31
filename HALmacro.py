import re
import imp
import time
import uuid
import random
import socket
import urllib2
import os.path
import traceback
from glob import glob
from getpass import getuser

from HALapi import get_main_dir

def get_ip():
    try:
        return urllib2.urlopen('http://automation.whatismyip.com/n09230945.asp').read().strip()
    except urllib2.HTTPError:
        return socket.gethostbyname(socket.gethostname())

def get_location():
    page = urllib2.urlopen('http://www.tracemyip.org').read().replace('&nbsp;', '')
    recity = re.compile('<td valign="top" class="tID_01"><b>Hub City:</b>(.*?)<br>', re.S)
    reloc = re.compile('<td class="tID_01"><b>State:</b></td>(.*?)</tr>', re.S)
    reclean = re.compile('<.*?>') 
    city = reclean.sub('', recity.search(page).group(1).replace(' ', '')).strip()
    location = reclean.sub('', reloc.search(page).group(1).replace(' ', '')).strip()
    return '%s, %s'%(city, location)

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
            '$IP$'            : get_ip(),
            '$LOCATION$'      : get_location(),
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
        
        # Plugin interface
        dir = os.path.join(get_main_dir(), 'plugins/macro')
        files = os.path.join(dir, '*.py')
        files = [os.path.basename(i).replace('.py', '') for i in glob(files)]
        for file in files:
            try:
                data = imp.find_module(file, [dir])
                module = imp.load_module(str(uuid.uuid1()), *data)
                if hasattr(module, 'basic'):
                    self.basic.update(module.basic)
                if hasattr(module, 'extended'):
                    self.extended.update(module.extended)
            except:
                print 'Error in macro extension', file
                traceback.print_exc()
        #for i, j in self.extended.iteritems():
        #    print i.pattern, ':', j
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
