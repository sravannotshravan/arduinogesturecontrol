@echo off
REM Quick Start Script for Windows - Simulation Mode
REM This script sets up and runs the simulation on Windows

echo ========================================
echo Gesture Control System - Quick Start
echo ========================================
echo.

REM Check if virtual environment exists
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment
        echo Make sure Python 3.8+ is installed
        pause
        exit /b 1
    )
    echo Virtual environment created successfully!
    echo.
)

REM Activate virtual environment and install packages
echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo Checking/Installing required packages...
pip install opencv-python mediapipe numpy --quiet
if errorlevel 1 (
    echo Error: Failed to install packages
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup complete!
echo ========================================
echo.
echo Select a program to run:
echo   1. Arduino Client (USB Serial - laptop + Arduino)
echo   2. Simulation Mode (visualize LED and Motor)
echo   3. Gesture Testing (test detection accuracy)
echo   4. Exit
echo.

choice /c 1234 /n /m "Enter your choice (1-4): "

if errorlevel 4 exit /b 0
if errorlevel 3 goto testing
if errorlevel 2 goto simulation
if errorlevel 1 goto arduino

:arduino
echo.
echo Starting Arduino USB Serial Client...
echo.
echo SETUP CHECKLIST:
echo [ ] Arduino connected via USB
echo [ ] Arduino code uploaded (gesture_control_arduino.ino)
echo [ ] LED connected to Arduino Pin 9
echo [ ] Servo motor connected to Arduino Pin 10
echo [ ] pyserial installed (pip install pyserial)
echo.
echo If not ready, press Ctrl+C to cancel
timeout /t 3
python gesture_control_client_arduino.py
goto end

:simulation
echo.
echo Starting Simulation Mode...
echo.
python gesture_control_simulation.py
goto end

:testing
echo.
echo Starting Gesture Testing...
echo.
python gesture_testing.py
goto end

:end
echo.
pause
