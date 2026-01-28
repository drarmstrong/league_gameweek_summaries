@echo off
REM Quick Start Script for FPL League Match Reports Streamlit App
REM This script sets up and runs the development environment

echo.
echo 🚀 FPL League Match Reports - Quick Start
echo ===========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH.
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✅ Python found: %PYTHON_VERSION%
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)

echo.
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat
echo ✅ Virtual environment activated
echo.

REM Install/upgrade pip
echo 📦 Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1
echo ✅ pip upgraded
echo.

REM Install dependencies
echo 📦 Installing dependencies from requirements.txt...
pip install -r requirements.txt
echo ✅ Dependencies installed
echo.

REM Check if config files exist
if not exist "fpl_data\config.json" (
    echo ⚠️  fpl_data\config.json not found
    echo    Copy from fpl_data\config_template.json and edit with your settings
)

if not exist "fpl_data\bios.json" (
    echo ⚠️  fpl_data\bios.json not found
    echo    Copy from fpl_data\bios_template.json and edit with your team info
)

echo.
echo ===========================================
echo 🎉 Setup complete!
echo ===========================================
echo.
echo To start the Streamlit app, run:
echo    streamlit run app.py
echo.
echo The app will open at: http://localhost:8501
echo.
echo Press Ctrl+C to stop the server when done.
echo.
pause
