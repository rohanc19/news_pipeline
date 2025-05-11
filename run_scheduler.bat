@echo off
echo Starting News Pipeline Scheduler...
start /B python scheduler.py --interval 30 --output-dir outputs > scheduler_output.log 2>&1
echo Scheduler started in the background. Check scheduler.log and scheduler_output.log for details.
