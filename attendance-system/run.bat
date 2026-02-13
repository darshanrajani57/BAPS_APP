@echo off
REM BAPS Attendance System - Windows Launcher
REM This script automatically sets up and runs the application

echo.
echo ========================================
echo BAPS Attendance Management System
echo Windows Launcher
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    echo Remember to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [OK] Python is installed
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
    echo.
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo [OK] Virtual environment activated
echo.

REM Install/Update dependencies
echo [INFO] Checking and installing dependencies...
pip install -q --upgrade pip
pip install -q -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    echo Please run: pip install -r requirements.txt
    pause
    exit /b 1
)
echo [OK] Dependencies installed
echo.

REM Run the application
echo ========================================
echo Starting BAPS Attendance System...
echo ========================================
echo.
echo Open your browser and go to:
echo http://localhost:5000
echo.
echo Press CTRL+C to stop the server
echo ========================================
echo.

python app.py

pause
