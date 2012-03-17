@echo off
setup.py
cd HAL
:: zip -r9X HAL-%VERSION%.zip data\* inputLogic\* *.dll HALstart.bat -x data\temp\* data\old\*
7za a HAL