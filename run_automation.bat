@echo off
title YouTube Shorts Automation

echo ========================================
echo    YouTube Shorts Automation System
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo Python detected: 
python --version
echo.

REM Check if this is first run
if not exist "config.json" (
    echo First time setup detected...
    echo Running setup script...
    echo.
    python setup.py
    echo.
    echo Setup complete! Please configure your YouTube API credentials.
    echo Edit client_secrets_template.json with your credentials and rename to client_secrets.json
    echo.
    pause
    exit /b 0
)

REM Check if client_secrets.json exists
if not exist "client_secrets.json" (
    echo Error: client_secrets.json not found
    echo Please set up your YouTube API credentials first
    echo Run setup.py for instructions
    pause
    exit /b 1
)

echo Starting YouTube Shorts Automation...
echo Press Ctrl+C to stop
echo.

REM Ask user what they want to do
echo What would you like to do?
echo 1. Run test (create one video without uploading)
echo 2. Start daily automation
echo 3. Check configuration
echo 4. View recent uploads
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo Running test mode...
    python main.py --test
) else if "%choice%"=="2" (
    echo Starting daily automation...
    echo This will run continuously. Press Ctrl+C to stop.
    python main.py
) else if "%choice%"=="3" (
    echo Checking configuration...
    python config.py
) else if "%choice%"=="4" (
    echo Checking recent uploads...
    python youtube_uploader.py
) else (
    echo Invalid choice. Starting daily automation...
    python main.py
)

echo.
echo Automation stopped.
pause
