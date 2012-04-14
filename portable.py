from distutils.core import setup
import py2exe
from glob import glob
import sys
import os
import msvcrt
sys.argv.append('py2exe')

setup(console=['HALcon.py', 'HALguicon.py'], windows=['HALgui.pyw'],
      data_files=[('data', glob('data/*.hal')+glob('data/*.chal')+glob('data/element.db')),
                  ('', ['Buffering.png', 'Logo_V1.png', 'Normal.png'])],
      options={
        'py2exe': {'ascii': False, 'dist_dir': 'portable', 'optimize': 2,
                   'excludes': ['_ssl', 'unittest', 'doctest', 'inspect', 'Tkinter'],
                   'includes': ['sqlite3'],
                   },
      }
)

os.chdir('portable')
os.system('ren HALcon.exe HAL.exe')

open('python27.dll', 'wb').write(open('..\\python27.dll', 'rb').read())
