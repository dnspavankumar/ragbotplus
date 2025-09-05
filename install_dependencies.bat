@echo off
echo ================================================================
echo Gmail RAG Assistant - Windows Setup
echo Installing Python dependencies...
echo ================================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Upgrade pip first
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies using the setup script
echo.
echo Running setup script...
python setup.py

echo.
echo ================================================================
echo Setup completed!
echo.
echo Next steps:
echo 1. Get Gmail API credentials (credentials.json)
echo 2. Get Groq API key from console.groq.com
echo 3. Run: python main.py
echo ================================================================
pause