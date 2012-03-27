import sys
import os
import os.path
import subprocess

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

espeak_dir  = os.path.join(get_main_dir(), 'espeak')
espeak_path = os.path.join(espeak_dir, 'espeak.exe')
if os.name == 'nt':
    null_file = open('nul', 'w')
else:
    null_file = open('/dev/null', 'w')

def stop_speaking(handle):
    if handle is None:
        return
    try:
        handle.terminate()
    except OSError:
        pass

def speak(text, block=True):
    cmd = [espeak_path, '-v', 'en-us', text]
    if block:
        return not subprocess.call(cmd, stdin=null_file, stdout=null_file, stderr=null_file)
    else:
        return subprocess.Popen(cmd, stdin=null_file, stdout=null_file, stderr=null_file)

if __name__ == '__main__':
    speak("Open a file, returning an object of the file type described in section File Objects. If the file cannot be opened, IOError is raised. When opening a file, it's preferable to use open() instead of invoking the file constructor directly.", False)
