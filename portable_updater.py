import os 
import urllib2 
from decimal import Decimal 
import subprocess
import sys

format = 'http://dl.dropbox.com/u/67341745/HAL_PE_%.3f.7z' 

try:  
   f = open("Version.halconfig")  
   version = current = Decimal(f.read()) 
except IOError: 
    version = current = Decimal('0.010') 

incre = Decimal('0.001') 
while True: 
   try: 
       u = urllib2.urlopen(format%version) 
   except urllib2.HTTPError as e: 
       version -= incre 
       break 
   else: 
       u.close()     
       version += incre 

if version == current: 
    subprocess.call(['HAL'])
    raise SystemExit

url = format % version 
file_name = url.split('/')[-1] 
u = urllib2.urlopen(url) 
f = open(file_name, 'wb') 
meta = u.info() 
file_size = int(meta.getheaders("Content-Length")[0]) 
print '---' 
print 'Found update: ' + file_name 
print '  Downloading: %s Size: %s' % (file_name, file_size) 

file_size_dl = 0 
block_sz = 8192 
while True: 
   buffer = u.read(block_sz) 
   if not buffer: 
       break 
   file_size_dl += len(buffer) 
   f.write(buffer) 
   status = ' Downloaded: %10d [%3.2f%%]\r' % (file_size_dl, file_size_dl * 100. / file_size) 
   status = status + chr(8)*(len(status)+1) 
   print status, 

f.close() 

print '--Extracting--'
subprocess.call(['extract', file_name]) 
os.remove(file_name)
print '--Finished--'

print 'Rebooting...'

os.system(['clear','cls'][os.name == 'nt'])

subprocess.call(['HAL'])