@echo off
echo Stopping News Pipeline Scheduler...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq scheduler.py"
echo Scheduler stopped.
