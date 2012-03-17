@echo off
if not exist releases mkdir releases
set /p VERSION=<latest.txt
del /q compact
md compact

compact.py

cd compact
7za a -sfx HAL_CE_%VERSION%.exe *
del ..\releases\HAL_CE_%VERSION%.exe
move HAL_CE_%VERSION%.exe ..\releases
echo Done