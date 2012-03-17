@echo off
if not exist releases mkdir releases
set /p VERSION=<latest.txt
del /q standard
md standard

echo Copy bytecode file...
copy equation.py standard
copy HALBot.py standard
copy HALcon.py standard
copy HALdatetime.py standard
copy HALformat.py standard
copy HALmain.py standard
copy boost_python-vc100-mt-1_47.dll standard
copy HALnative.pyd standard
python -O -m compileall standard -q

cd standard
mkdir data
copy ..\data\*.hal data
copy ..\data\*.chal data
del *.py
copy ..\latest.txt Version.halconfig

7za a HAL_SE_%VERSION%.7z *
del ..\releases\HAL_SE_%VERSION%.7z
move HAL_SE_%VERSION%.7z ..\releases
echo Done
