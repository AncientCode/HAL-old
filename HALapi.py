import sys
import os.path
import platform
import datetime

def get_main_dir():
    if main_is_frozen():
        return os.path.dirname(sys.executable)
    for dirname in sys.path:
        if os.path.exists(os.path.join(dirname, __file__)):
            return dirname

def get_system_info():
    if os.name == 'nt':
        ver, build, sp, type = platform.win32_ver()
        arch = platform.machine()
        pyver = platform.python_version()
        impl = platform.python_implementation()
        return 'Windows {ver} {sp}, NT {build} on {arch} Python {pyver} ({impl}).'.format(ver=ver, sp=sp, build=build, arch=arch, pyver=pyver, impl=impl)

def main_is_frozen():
    import imp
    return (hasattr(sys, "frozen") or # new py2exe
            hasattr(sys, "importers") # old py2exe
            or imp.is_frozen("__main__")) # tools/freeze

def module_filter(name):
    if not os.path.exists(name):
        return False
    if name[-3:].lower() == '.py':
        return os.path.basename(name)[:-3]
    elif os.path.isdir(name) and os.path.isfile(os.path.join(name, '__init__.py')):
        return os.path.basename(name)

class HALException(Exception): pass
class HALcannotHandle(HALException): pass

maindir = get_main_dir()
datadir = os.path.join(maindir, 'data')

def clean_string(text, proper_letters=None):
    if proper_letters is None:
        proper_letters = ' 0123456789abcdefghijklmnopqrstuvwxyz'
    letters = bytearray()
    for letter in text.lower():
        if letter in proper_letters:
            letters.append(letter)
    return str(letters)

def age_from_dob(dob):
    today = datetime.date.today()
    day = today.replace(year=dob.year)
    age = today.year - dob.year
    if dob > day:
        age -= 1
    return age
