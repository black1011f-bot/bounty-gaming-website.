@echo off
setlocal
cd /d "%~dp0"
py -3 -m pip install -r requirements.txt
if errorlevel 1 (
  echo Could not install dependencies. Install Python 3.10+ first.
  pause
  exit /b 1
)
py -3 bounty_dex.py
if errorlevel 1 pause
endlocal
