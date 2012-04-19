import re
import imp
import time
import uuid
import random
import os.path
import datetime
import traceback
from glob import glob
from getpass import getuser

from HALapi import get_main_dir, module_filter

class HALmacro(object):
    rerandint = re.compile(r'\$RANDINT@(-?[0-9]+?)~(-?[0-9]+?)\$')
    halbday = datetime.date(1998, 3, 9)
    def __init__(self, parent, user=None, write=False):
        self.basic = {
            '$USERNAME$'      : user if user is not None else getuser(),
            '$USER$'          : user if user is not None else getuser(),
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
            '$BIRTHDAY$'      : self.halbday.strftime('%B %d, %Y'),
            '$AGE$'           : lambda: str((datetime.date.today()-self.halbday).days//365),
        }
        self.extended = {
            self.rerandint:   lambda m: str(random.randint(int(m.group(1)), int(m.group(2)))),
        }
        self.hal = parent
        
        # Plugin interface
        dir = os.path.join(get_main_dir(), 'plugins/macro')
        files = filter(bool, map(module_filter, glob(os.path.join(dir, '*'))))
        for file in files:
            if write:
                print 'Loading macro extension "%s"...'%file
            try:
                data = imp.find_module(file, [dir])
                module = imp.load_module(str(uuid.uuid1()), *data)
                if hasattr(module, 'basic'):
                    self.basic.update(module.basic)
                if hasattr(module, 'extended'):
                    self.extended.update(module.extended)
                if hasattr(module, 'halfiles'):
                    for file in module.halfiles:
                        self.hal.load(file)
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
                input = input.replace(macro, replacement() if callable(replacement) else replacement)
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
