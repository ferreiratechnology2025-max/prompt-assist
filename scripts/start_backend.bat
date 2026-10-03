@echo off
echo Starting QualiPrompt Backend...
cd /d D:\prompt_Assist\backend
call venv\Scripts\activate 2>nul || echo [INFO] Virtual env not found, using system Python
python run.py
pause
