@echo off
REM Schedule LP Alerts 24H to run daily at 8:00 AM for Windows
REM Run this as Administrator

setlocal enabledelayedexpansion

REM Get the script directory
set SCRIPT_DIR=%~dp0
set PYTHON_PATH=%SCRIPT_DIR%venv\Scripts\python.exe

REM Check if virtual environment exists
if not exist "%PYTHON_PATH%" (
    echo.
    echo Error: Virtual environment not found
    echo Please run: python -m venv venv
    echo.
    pause
    exit /b 1
)

REM Check if running as Administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo.
    echo Error: This script must be run as Administrator
    echo Please right-click CMD and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

REM Create the task
echo Creating scheduled task LP_Alerts_24H...
schtasks /create /tn "LP_Alerts_24H" /tr "%PYTHON_PATH% %SCRIPT_DIR%main.py" /sc daily /st 08:00 /ru SYSTEM /f

if %errorLevel% equ 0 (
    echo.
    echo Success! Task created.
    echo LP Alerts will run daily at 08:00 AM
    echo.
    echo View task: schtasks /query /tn "LP_Alerts_24H" /v
    echo Delete task: schtasks /delete /tn "LP_Alerts_24H" /f
    echo.
) else (
    echo.
    echo Error: Failed to create task
    echo Run as Administrator
    echo.
    pause
    exit /b 1
)

pause
