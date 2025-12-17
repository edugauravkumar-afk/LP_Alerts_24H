@echo off
REM Schedule LP Alerts 24H to run daily at 8:00 AM for Windows
REM Run this as Administrator

setlocal enabledelayedexpansion

REM Get the script directory
set SCRIPT_DIR=%~dp0
set PYTHON_PATH=%SCRIPT_DIR%venv\Scripts\python.exe

REM Check if virtual environment exists
if not exist "%PYTHON_PATH%" (
    echo ❌ Virtual environment not found at %PYTHON_PATH%
    echo Please run: bash setup.sh
    pause
    exit /b 1
)

REM Check if running as Administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ This script must be run as Administrator
    echo Please right-click and select "Run as Administrator"
    pause
    exit /b 1
)

REM Create the task
echo Creating scheduled task "LP_Alerts_24H"...
schtasks /create ^
    /tn "LP_Alerts_24H" ^
    /tr "%PYTHON_PATH% %SCRIPT_DIR%main.py" ^
    /sc daily ^
    /st 08:00 ^
    /ru SYSTEM ^
    /f

if %errorLevel% equ 0 (
    echo ✅ Task created successfully!
    echo 🕐 LP Alerts will run daily at 08:00 AM UTC
    echo.
    echo To view the task:
    echo   schtasks /query /tn "LP_Alerts_24H" /v
    echo.
    echo To delete the task:
    echo   schtasks /delete /tn "LP_Alerts_24H" /f
) else (
    echo ❌ Failed to create task
    echo This script must be run as Administrator
    pause
    exit /b 1
)

pause
