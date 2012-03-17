from distutils.core import setup
import py2exe
from glob import glob
import sys
import os
import msvcrt
sys.argv.append('py2exe')

setup(console=['portable_updater.py'], zipfile="shared.lib",
      options={
        'py2exe': {'ascii': True, 'dist_dir': 'updater', 'optimize': 2,
                   'excludes': ['_ssl', 'unittest', 'doctest', 'difflib', 'inspect'],
                   },
      }
)

open('updater\\python27.dll', 'wb').write(open('python27.dll', 'rb').read())
