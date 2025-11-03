# Employee Monitoring System - Windows Installation Script
# Run this script in PowerShell as Administrator

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Employee Monitoring System - Installation" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
    
    # Check version
    if ($pythonVersion -match "Python (\d+)\.(\d+)") {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]
        
        if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 8)) {
            Write-Host "ERROR: Python 3.8 or later required!" -ForegroundColor Red
            Write-Host "Please install Python from https://www.python.org/downloads/" -ForegroundColor Yellow
            exit 1
        }
    }
} catch {
    Write-Host "ERROR: Python not found!" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
    exit 1
}

# Create virtual environment
Write-Host ""
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "Virtual environment already exists, skipping..." -ForegroundColor Green
} else {
    python -m venv venv
    Write-Host "Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host ""
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Upgrade pip
Write-Host ""
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install dependencies
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
Write-Host "(This may take several minutes, especially for dlib and face_recognition)" -ForegroundColor Cyan

# Try to install from requirements
try {
    pip install -r requirements.txt
    Write-Host "All dependencies installed successfully!" -ForegroundColor Green
} catch {
    Write-Host "WARNING: Some packages may have failed to install" -ForegroundColor Yellow
    Write-Host "This is common for dlib and face_recognition on Windows" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "If you encounter issues:" -ForegroundColor Cyan
    Write-Host "1. Install Visual Studio Build Tools" -ForegroundColor White
    Write-Host "2. Or use pre-built wheels from: https://github.com/jloh02/dlib" -ForegroundColor White
    Write-Host "3. Or disable face recognition in config.yaml" -ForegroundColor White
}

# Create necessary directories
Write-Host ""
Write-Host "Creating directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "data" | Out-Null
New-Item -ItemType Directory -Force -Path "logs" | Out-Null
Write-Host "Directories created" -ForegroundColor Green

# Check if config.yaml exists
Write-Host ""
if (!(Test-Path "config.yaml")) {
    Write-Host "WARNING: config.yaml not found!" -ForegroundColor Yellow
    Write-Host "Please ensure config.yaml is in the project directory" -ForegroundColor Yellow
} else {
    Write-Host "Configuration file found" -ForegroundColor Green
}

# Installation complete
Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "To start the system:" -ForegroundColor Cyan
Write-Host "1. Activate virtual environment: .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "2. Run the application: python main.py" -ForegroundColor White
Write-Host "3. Open browser to: http://localhost:5000" -ForegroundColor White
Write-Host ""
Write-Host "For help, see README.md" -ForegroundColor Yellow
Write-Host ""
