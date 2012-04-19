import re
import time
import os.path

redate     = re.compile(r'\$DATE\$')
retime     = re.compile(r'\$TIME\$')
redatetime = re.compile(r'\$DATETIME\$')
reisotime  = re.compile(r'\$ISOTIME\$')
readvdate  = re.compile(r'\$DATE\+(-?[0-9]+?)\$')
readvtime  = re.compile(r'\$TIME\+(-?[0-9]+?)\$')
readvdtime = re.compile(r'\$DATETIME\+(-?[0-9]+?)\$')
readvitime = re.compile(r'\$ISOTIME\+(-?[0-9]+?)\$')
rerandint  = re.compile(r'\$RANDINT@(-?[0-9]+?)~(-?[0-9]+?)\$')

extended = {
    redate:     lambda m: time.strftime('%B %d, %Y'),
    retime:     lambda m: time.strftime('%H:%M:%S'),
    redatetime: lambda m: time.strftime('%H:%M:%S on %B %d, %Y'),
    reisotime:  lambda m: time.strftime('%Y-%m-%dT%H:%M:%S'),
    readvdate:  lambda m: time.strftime('%B %d, %Y', time.localtime(time.time()+int(m.group(1)))),
    readvtime:  lambda m: time.strftime('%H:%M:%S',  time.localtime(time.time()+int(m.group(1)))),
    readvdtime: lambda m: time.strftime('%H:%M:%S on %B %d, %Y', time.localtime(time.time()+int(m.group(1)))),
    readvitime: lambda m: time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(time.time()+int(m.group(1)))),
}

halfiles = [os.path.join(os.path.dirname(__file__), 'datetime.hal')]
