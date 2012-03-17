import HALmain
from HALBot import HAL
import urllib2
from decimal import Decimal

def main():
    format = 'http://dl.dropbox.com/u/67341745/HAL_CE_%.3f.exe' 

    version = current = Decimal(HAL.version) 

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

    if version != current: 
        try:
            u = urllib2.urlopen(format%version) 
        except urllib2.HTTPError as e:
            pass
        else:
            u.close()
            url = format % version
            print 'New version found at:'
            print '  ', url
            print 'Please upgrade as soon as possible.'
            print
    HALmain.main()

if __name__ == '__main__':
    main()