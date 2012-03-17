@echo off
if not exist releases mkdir releases
set /p VERSION=<latest.txt
del /q portable
md portable

portable.py

cd portable
copy ..\latest.txt Version.halconfig

7za a HAL_PE_%VERSION%.7z *
del ..\releases\HAL_PE_%VERSION%.7z
move HAL_PE_%VERSION%.7z ..\releases
echo Done
