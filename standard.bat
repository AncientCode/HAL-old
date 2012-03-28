@echo off
if not exist releases mkdir releases
set /p VERSION=<latest.txt
del /q standard
md standard

echo Copy bytecode file...
cp -r equation.py HALBot.py HALcon.py HALwiki.py HALapi.py HALformat.py HALmain.py HALmacro.py HALspeak.py boost_python-vc100-mt-1_47.dll HALnative.pyd HALgui.py HALgui.pyw espeak standard
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
