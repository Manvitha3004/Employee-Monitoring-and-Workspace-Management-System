# Employee Monitoring System - Startup Script
# Double-click this file to start the system

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Employee Monitoring System" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (!(Test-Path "venv")) {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run install.ps1 first" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Check if config exists
if (!(Test-Path "config.yaml")) {
    Write-Host "ERROR: config.yaml not found!" -ForegroundColor Red
    Write-Host "Please ensure config.yaml is in the project directory" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Start the system
Write-Host ""
Write-Host "Starting Employee Monitoring System..." -ForegroundColor Green
Write-Host ""
Write-Host "Access the web interface at: http://localhost:5000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the system" -ForegroundColor Yellow
Write-Host ""

# Run the application
python main.py

# Deactivate virtual environment on exit
deactivate
