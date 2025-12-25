@echo off
setlocal enabledelayedexpansion

:: Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
set "PYTHON_PATH=%SCRIPT_DIR%venv\Scripts\python.exe"

echo Creating scheduled task LP_Alerts_24H...

:: Create scheduled task to run daily at 8:00 AM (initially disabled)
schtasks /create /tn "LP_Alerts_24H" /tr "\"%PYTHON_PATH%\" \"%SCRIPT_DIR%main.py\"" /sc daily /st 08:00 /f /rl highest

if %errorlevel% == 0 (
    echo.
    echo Success! Task created.
    echo LP Alerts will run daily at 08:00 AM
    echo.
    echo View task: schtasks /query /tn "LP_Alerts_24H" /v
    echo Delete task: schtasks /delete /tn "LP_Alerts_24H" /f
    echo Enable task: schtasks /change /tn "LP_Alerts_24H" /enable
    echo Disable task: schtasks /change /tn "LP_Alerts_24H" /disable
) else (
    echo Failed to create scheduled task.
    exit /b 1
)

echo.
pause