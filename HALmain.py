from HALBot import HAL
import os.path
import sys
import os
import codecs
from HALapi import get_main_dir, get_system_info

def main(data=None):
    sys.stdout = codecs.getwriter('mbcs')(sys.stdout, 'replace')
    if data is None:
        data = os.path.join(get_main_dir(), 'data')
    if not os.path.exists(data):
        raise SystemExit('Your need a full package with the data folder')
    print '[SYSTEM]', 'Booted on', get_system_info(), '[/SYSTEM]'
    print
    print '[SYSTEM]'
    hal = HAL(write=True, speak=True)
    print '[/SYSTEM]'
    print
    print '-HAL: Hello %s. I am HAL %s.'%(hal.user, hal.version)
    print
    prompt = '-%s:'%hal.user
    halpro = '-HAL:'
    length = max(len(prompt), len(halpro))
    if len(prompt) < length:
        prompt += ' '*(length-len(prompt))
    if len(halpro) < length:
        halpro += ' '*(length-len(halpro))
    prompt += ' '
    try:
        while hal.running:
            line = raw_input(prompt)
            for i in hal.ask(line):
                print halpro, i
            print
        raise EOFError
    except EOFError:
        print '-HAL:', hal.shutdown()

if __name__ == '__main__':
    main()
