#!/bin/bash
# Quick Start Script for Raspberry Pi - Real Hardware Control
# This script sets up and runs the gesture control system

echo "========================================"
echo "Gesture Control System - Raspberry Pi"
echo "========================================"
echo ""

# Check if running on Raspberry Pi
if [ ! -f /proc/device-tree/model ]; then
    echo "Warning: This doesn't appear to be a Raspberry Pi"
    echo "For simulation mode, run gesture_control_simulation.py instead"
    echo ""
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment"
        echo "Make sure Python 3.8+ is installed"
        exit 1
    fi
    echo "Virtual environment created successfully!"
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install/upgrade packages
echo ""
echo "Checking/Installing required packages..."
pip install --upgrade pip setuptools wheel
pip install opencv-python mediapipe numpy RPi.GPIO
if [ $? -ne 0 ]; then
    echo "Error: Failed to install packages"
    exit 1
fi

echo ""
echo "========================================"
echo "Setup complete!"
echo "========================================"
echo ""
echo "Select a program to run:"
echo "  1. Real Hardware Control (Raspberry Pi)"
echo "  2. Simulation Mode"
echo "  3. Gesture Testing"
echo "  4. Exit"
echo ""

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo ""
        echo "Starting Hardware Control System..."
        echo "Make sure your LED and Servo are connected:"
        echo "  - LED: GPIO 18 (Pin 12)"
        echo "  - Servo: GPIO 13 (Pin 33)"
        echo ""
        python gesture_control_system.py
        ;;
    2)
        echo ""
        echo "Starting Simulation Mode..."
        echo ""
        python gesture_control_simulation.py
        ;;
    3)
        echo ""
        echo "Starting Gesture Testing..."
        echo ""
        python gesture_testing.py
        ;;
    4)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "Done!"
