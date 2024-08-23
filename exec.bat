@echo off
REM cd to required directory
cd /d "%~dp0"

REM execute python script
python.exe Logger-Concat.py

REM pause window to stay open after script ends
pause
