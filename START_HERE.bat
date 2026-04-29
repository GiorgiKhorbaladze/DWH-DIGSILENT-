@echo off
cd /d %~dp0

echo ======================================
echo DWH-DIGSILENT მარტივი გაშვება

echo ======================================

echo.
set /p DWH_API_KEY=ჩასვი DWH_API_KEY და დააჭირე Enter: 

echo.
echo ვუშვებ პროცესს...
python legacy_py27.py

echo.
echo დასრულდა. თუ error იყო, ფანჯარაში ნახავ დეტალს.
pause
