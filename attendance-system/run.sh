#!/bin/bash

# BAPS Attendance System - Mac/Linux Launcher
# This script automatically sets up and runs the application

echo ""
echo "========================================"
echo "BAPS Attendance Management System"
echo "Mac/Linux Launcher"
echo "========================================"
echo ""

# Check if Python3 is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 is not installed"
    echo ""
    echo "Please install Python 3.8+ from https://www.python.org/downloads/"
    echo "Or use Homebrew: brew install python@3.11"
    exit 1
fi

echo "[OK] Python3 is installed"
python3 --version
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "[INFO] Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment"
        exit 1
    fi
    echo "[OK] Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "[INFO] Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment"
    exit 1
fi
echo "[OK] Virtual environment activated"
echo ""

# Install/Update dependencies
echo "[INFO] Checking and installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    echo "Please run: pip install -r requirements.txt"
    exit 1
fi
echo "[OK] Dependencies installed"
echo ""

# Run the application
echo "========================================"
echo "Starting BAPS Attendance System..."
echo "========================================"
echo ""
echo "Open your browser and go to:"
echo "http://localhost:5000"
echo ""
echo "Press CTRL+C to stop the server"
echo "========================================"
echo ""

python3 app.py
