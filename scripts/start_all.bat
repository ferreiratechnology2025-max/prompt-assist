@echo off
echo Starting QualiPrompt...
start "QualiPrompt Backend" cmd /k scripts\start_backend.bat
timeout /t 3 /nobreak >nul
start "QualiPrompt Frontend" cmd /k scripts\start_frontend.bat
echo.
echo Backend:  http://localhost:8000/docs
echo Frontend: http://localhost:5173
echo.
