import sys
import os.path
import platform

def get_main_dir():
    if main_is_frozen():
        return os.path.dirname(sys.executable)
    for dirname in sys.path:
        if os.path.exists(os.path.join(dirname, __file__)):
            return dirname

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

class HALException(Exception): pass
class HALcannotHandle(HALException): pass

maindir = get_main_dir()
datadir = os.path.join(maindir, 'data')
