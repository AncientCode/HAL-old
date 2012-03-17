from HALBot import HAL
import os.path
import sys
import os
import platform

def get_system_info():
    if os.name == 'nt':
        ver, sp, build, type = platform.win32_ver()
        arch = platform.machine()
        pyver = platform.python_version()
        impl = platform.python_implementation()
        return 'Windows {ver} {sp}, NT {build} on {arch} Python {pyver} ({impl}).'.format(ver=ver, sp=sp, build=build, arch=arch, pyver=pyver, impl=impl)

def main_is_frozen():
    import imp
    return (hasattr(sys, "frozen") or # new py2exe
            hasattr(sys, "importers") # old py2exe
            or imp.is_frozen("__main__")) # tools/freeze
def get_main_dir():
    if main_is_frozen():
        return os.path.dirname(sys.executable)
    for dirname in sys.path:
        if os.path.exists(os.path.join(dirname, __file__)):
            return dirname

def main(data=None):
    if data is None:
        data = os.path.join(get_main_dir(), 'data')
    if not os.path.exists(data):
        raise SystemExit('Your need a full package with the data folder')
    print '[SYSTEM]', 'Booted on', get_system_info(), '[/SYSTEM]'
    print
    print '[SYSTEM]'
    hal = HAL(write=True)
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
