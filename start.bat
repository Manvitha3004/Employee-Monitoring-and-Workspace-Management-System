@echo off
REM Employee Monitoring System - Windows Batch Launcher
REM For users who prefer batch files over PowerShell

echo ================================================
echo Employee Monitoring System
echo ================================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo ERROR: Virtual environment not found!
    echo Please run install.ps1 first
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if config exists
if not exist "config.yaml" (
    echo ERROR: config.yaml not found!
    pause
    exit /b 1
)

echo Starting Employee Monitoring System...
echo.
echo Access the web interface at: http://localhost:5000
echo.
echo Press Ctrl+C to stop the system
echo.

REM Run the application
python main.py

REM Deactivate on exit
call venv\Scripts\deactivate.bat
