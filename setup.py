from distutils.core import setup
import py2exe
from glob import glob
import sys
import os
import msvcrt
sys.argv.append('py2exe')

setup(console=['HALcon.py'],
      options={
        'py2exe': {'data_files': [('data', glob('data/*.hal')+glob('data/*.chal'))]
                   'ascii': True, 'dist_dir': 'HAL',
                   'excludes': ['_ssl', 'unittest', 'doctest', 'difflib', 'inspect'],
                   },
      }
)

os.chdir('HAL')
os.system('ren HALcon.exe HAL.exe')
#os.system('7za')

sys.stderr.write('Press any key to continue...')
msvcrt.getch()
