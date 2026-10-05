@echo off
REM YouTube Hub - Windows: bu dosyaya cift tikla. Panel tarayicida acilir.
cd /d "%~dp0\.."
git pull --ff-only -q 2>nul
where py >nul 2>nul
if %errorlevel%==0 (py -3 youtube-hub\hub.py serve) else (python youtube-hub\hub.py serve)
pause
