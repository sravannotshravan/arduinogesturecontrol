# 🎮 Gesture-Controlled LED & Servo System - Project Summary

## 📋 Project Overview

This project implements a complete gesture-controlled system for Raspberry Pi 5 that uses hand gestures detected via camera to control an LED and a servo motor. The system includes three different programs for hardware control, simulation, and testing.

---

## 📁 Created Files

### Main Programs

1. **`gesture_control_system.py`** ⭐ (Raspberry Pi Hardware)
   - Full hardware control with RPi.GPIO
   - Controls real LED and servo motor
   - LED: GPIO 18 (Pin 12) with PWM brightness control
   - Servo: GPIO 13 (Pin 33) with PWM angle control
   - Requires Raspberry Pi with camera

2. **`gesture_control_simulation.py`** 💻 (Any Computer)
   - Visual simulation without hardware
   - Shows LED glow effects with brightness levels
   - Shows servo arm rotation with angle display
   - Split-screen: camera feed + device visualization
   - Perfect for testing before hardware deployment

3. **`gesture_testing.py`** 🧪 (Any Computer)
   - Pure gesture detection testing
   - Real-time statistics and accuracy tracking
   - Gesture hold time measurement
   - Finger count display
   - Detection counter for each gesture

4. **`hand_gesture_detection.py`**
   - Original basic gesture detection demo
   - Shows all 6 gestures without device control

### Documentation

5. **`README_SYSTEM.md`**
   - Complete system documentation
   - Installation instructions for both Raspberry Pi and Windows/Mac
   - Usage guide for all three programs
   - Troubleshooting section
   - Customization options

6. **`WIRING_GUIDE.md`**
   - Detailed hardware wiring instructions
   - ASCII circuit diagrams
   - GPIO pinout reference
   - Component testing procedures
   - Safety checklist

7. **`README.md`** (Original)
   - Basic hand gesture detection documentation

### Setup Files

8. **`requirements.txt`**
   - Python package dependencies
   - opencv-python, mediapipe, numpy, RPi.GPIO

9. **`quick_start.bat`** (Windows)
   - One-click setup and launch for Windows
   - Creates venv, installs packages, runs programs
   - Menu-driven interface

10. **`quick_start.sh`** (Linux/Raspberry Pi)
    - One-click setup and launch for Raspberry Pi
    - Creates venv, installs packages, runs programs
    - Menu-driven interface

---

## 🎯 Gesture Controls

### Mode Selection
| Gesture | Symbol | Function |
|---------|--------|----------|
| **Number 1** | ☝ | Switch to LED control mode |
| **Number 2** | ✌ | Switch to Motor control mode |

### Device Control
| Gesture | Symbol | Function |
|---------|--------|----------|
| **Open Hand** | ✋ | Turn current device ON |
| **Closed Fist** | ✊ | Turn current device OFF |
| **Thumbs Up** (hold 2s) | 👍 | Increase brightness/angle by 1 step |
| **Thumbs Down** (hold 2s) | 👎 | Decrease brightness/angle by 1 step |

---

## 🔌 Hardware Specifications

### LED Connection
- **GPIO Pin**: 18 (Physical Pin 12)
- **Component**: Any LED + 220Ω resistor
- **Control**: PWM brightness (5 levels: 20%, 40%, 60%, 80%, 100%)
- **Wiring**: GPIO 18 → LED Anode → 220Ω Resistor → LED Cathode → GND

### Servo Motor Connection
- **GPIO Pin**: 13 (Physical Pin 33)
- **Component**: Continuous Rotation Servo (FS90R, SM-S4303R, or modified SG90)
- **Control**: PWM speed control (5 levels: 20%, 40%, 60%, 80%, 100%)
- **Wiring**: 
  - Orange/Yellow → GPIO 13 (Signal)
  - Red → 5V (Power)
  - Brown/Black → GND (Ground)

**Important**: Uses continuous rotation servo, not standard positional servo. The motor rotates continuously when ON, and speed is controlled by PWM.

### Camera
- **Port**: CSI Camera Port on Raspberry Pi 5
- **Compatible**: Raspberry Pi Camera Module v2 or v3
- **Resolution**: 640x480 (configurable)

---

## 🚀 Quick Start Guide

### For Windows (Simulation/Testing)

```powershell
# Method 1: Use quick start script
.\quick_start.bat

# Method 2: Manual
cd "Gesture controlled LED and Motor"
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install opencv-python mediapipe numpy
python gesture_control_simulation.py
```

### For Raspberry Pi (Real Hardware)

```bash
# Method 1: Use quick start script
chmod +x quick_start.sh
./quick_start.sh

# Method 2: Manual
cd "Gesture controlled LED and Motor"
python3 -m venv .venv
source .venv/bin/activate
pip install opencv-python mediapipe numpy RPi.GPIO
python gesture_control_system.py
```

---

## 🎮 Usage Workflow

### Recommended Testing Sequence

1. **Step 1: Test Gestures** (Any Computer)
   ```bash
   python gesture_testing.py
   ```
   - Verify all 6 gestures are detected correctly
   - Check detection statistics
   - Practice gesture consistency

2. **Step 2: Try Simulation** (Any Computer)
   ```bash
   python gesture_control_simulation.py
   ```
   - See how gestures control the LED and motor
   - Understand the 5-level PWM control
   - Verify mode switching works
   - Practice the 2-second hold for thumbs up/down

3. **Step 3: Hardware Control** (Raspberry Pi Only)
   ```bash
   # Wire up hardware according to WIRING_GUIDE.md
   python gesture_control_system.py
   ```
   - Control real LED and servo motor
   - Adjust brightness and angle with gestures

---

## ⚙️ Technical Details

### PWM Control Levels

**LED Brightness (5 levels)**
| Level | Duty Cycle | Brightness |
|-------|-----------|------------|
| 1 | 20% | Dim |
| 2 | 40% | Low |
| 3 | 60% | Medium (default) |
| 4 | 80% | Bright |
| 5 | 100% | Maximum |

**Servo Rotation Speed (5 levels)**
| Level | Speed | Description |
|-------|-------|-------------|
| 1 | 20% | Slow rotation |
| 2 | 40% | Low-medium rotation |
| 3 | 60% | Medium rotation (default) |
| 4 | 80% | Fast rotation |
| 5 | 100% | Maximum speed |

**Note**: Motor continuously rotates when ON. Speed adjusts with levels.

### Gesture Hold Logic
- Thumbs up/down require 2-second continuous hold
- Prevents accidental triggers
- Visual countdown displayed on screen
- Can repeat by continuing to hold

---

## 📊 Features Comparison

| Feature | Testing | Simulation | Hardware |
|---------|---------|------------|----------|
| Gesture Detection | ✅ | ✅ | ✅ |
| Statistics Display | ✅ | ❌ | ❌ |
| LED Visualization | ❌ | ✅ | ✅ Real |
| Servo Visualization | ❌ | ✅ | ✅ Real |
| GPIO Control | ❌ | ❌ | ✅ |
| Runs on Windows | ✅ | ✅ | ❌ |
| Runs on Raspberry Pi | ✅ | ✅ | ✅ |
| Requires Hardware | ❌ | ❌ | ✅ |

---

## 🛠️ Troubleshooting

### Common Issues

1. **Camera not working**
   - Enable camera: `sudo raspi-config` → Interface → Camera
   - Check ribbon cable connection
   - Test: `libcamera-hello`

2. **GPIO permission denied**
   - Run with sudo: `sudo python gesture_control_system.py`
   - Or add to gpio group: `sudo usermod -a -G gpio $USER`

3. **Servo jittering**
   - Use external 5V power supply
   - Add capacitor across power pins
   - Check ground connections

4. **LED not working**
   - Verify polarity (long leg = positive)
   - Check resistor value (220Ω)
   - Test with multimeter

5. **Gestures not detected**
   - Ensure good lighting
   - Position hand clearly in frame
   - Adjust `min_detection_confidence` in code

6. **Virtual environment path errors (Windows)**
   - Use quotes around paths with spaces
   - Or use `quick_start.bat` script

---

## 🎯 Customization Options

### Change Detection Sensitivity
```python
self.hands = self.mp_hands.Hands(
    min_detection_confidence=0.7,  # 0.5-0.9 (lower = easier)
    min_tracking_confidence=0.5    # 0.5-0.9 (lower = smoother)
)
```

### Change Hold Duration
```python
HOLD_DURATION = 2.0  # Change to desired seconds
```

### Change GPIO Pins
```python
LED_PIN = 18      # Change to your pin
SERVO_PIN = 13    # Change to your pin
```

### Change PWM Frequency
```python
self.led_pwm = GPIO.PWM(self.LED_PIN, 1000)    # LED: 1000 Hz
self.servo_pwm = GPIO.PWM(self.SERVO_PIN, 50)  # Servo: 50 Hz
```

---

## 📚 Dependencies

### Required Python Packages
- **opencv-python** (4.8.1.78): Computer vision and camera access
- **mediapipe** (0.10.8): Hand landmark detection and tracking
- **numpy** (≥1.21.0): Numerical computations
- **RPi.GPIO** (≥0.7.1): Raspberry Pi GPIO control (Pi only)

### System Requirements
- **Raspberry Pi**: Raspberry Pi 5 with Raspberry Pi OS
- **Windows/Mac**: Python 3.8+ with webcam for simulation
- **Camera**: Raspberry Pi Camera Module or USB webcam
- **Python**: 3.8 or higher

---

## 🔒 Safety Notes

- ⚠️ Use appropriate resistors with LEDs (220Ω recommended)
- ⚠️ Servo motors can draw high current - use external power for multiple devices
- ⚠️ Don't exceed GPIO current limits (16mA per pin, 50mA total)
- ⚠️ Always disconnect power when wiring
- ⚠️ Verify polarity before connecting components

---

## 🎓 Learning Resources

### Understanding the Code
- **HandGestureDetector class**: MediaPipe hand tracking and gesture recognition
- **DeviceController class**: GPIO PWM control for LED and servo
- **DeviceSimulator class**: Visual representation of devices
- **Main loop**: Gesture processing and device control logic

### Key Concepts
- **MediaPipe Hands**: 21 hand landmarks per hand
- **PWM (Pulse Width Modulation)**: Control brightness/angle by varying duty cycle
- **Gesture hold detection**: Temporal filtering to prevent false triggers
- **Mode switching**: State machine for LED/Motor selection

---

## 📝 Next Steps

### Enhancements You Could Add
1. **More Gestures**: Add pinch, swipe, rotate gestures
2. **More Devices**: Control relays, buzzers, RGB LEDs
3. **Voice Feedback**: Add text-to-speech announcements
4. **Logging**: Record gesture usage statistics
5. **Web Interface**: Control via web dashboard
6. **Multiple Hands**: Support two-hand gestures
7. **Custom Training**: Train your own gesture classifier

### Project Ideas
- Smart home control system
- Robot arm controller
- Interactive art installation
- Accessibility interface
- Gaming controller
- Presentation remote

---

## 📄 File Structure Summary

```
Gesture controlled LED and Motor/
├── 🎮 Main Programs
│   ├── gesture_control_system.py       # Raspberry Pi hardware control
│   ├── gesture_control_simulation.py   # Visual simulation
│   ├── gesture_testing.py              # Gesture detection testing
│   └── hand_gesture_detection.py       # Original demo
│
├── 📚 Documentation
│   ├── README_SYSTEM.md                # Complete system guide
│   ├── WIRING_GUIDE.md                 # Hardware wiring instructions
│   ├── README.md                       # Original documentation
│   └── PROJECT_SUMMARY.md              # This file
│
├── 🔧 Setup Files
│   ├── requirements.txt                # Python dependencies
│   ├── quick_start.bat                 # Windows quick start
│   └── quick_start.sh                  # Linux/Pi quick start
│
└── 📁 Virtual Environment
    └── .venv/                          # Python virtual environment
```

---

## ✅ Project Completion Checklist

- [x] Hand gesture detection (6 gestures)
- [x] LED control with PWM (5 brightness levels)
- [x] Servo motor control with PWM (5 angle levels)
- [x] Mode switching (LED/Motor)
- [x] Gesture hold detection (2-second thumbs)
- [x] Real hardware control program (Raspberry Pi)
- [x] Visual simulation program (any computer)
- [x] Gesture testing program (any computer)
- [x] Complete documentation (README, wiring guide)
- [x] Quick start scripts (Windows and Linux)
- [x] Virtual environment configuration
- [x] GPIO pin specifications (18 for LED, 13 for Servo)
- [x] Safety considerations and warnings

---

## 🙏 Credits & Technologies

- **MediaPipe** by Google - Hand tracking and landmark detection
- **OpenCV** - Computer vision and camera interface
- **RPi.GPIO** - Raspberry Pi hardware control
- **Python** - Programming language
- **Raspberry Pi Foundation** - Hardware platform

---

## 📧 Support

For issues or questions:
1. Check the troubleshooting section in README_SYSTEM.md
2. Verify wiring against WIRING_GUIDE.md
3. Test gestures with gesture_testing.py first
4. Try simulation mode before hardware deployment

---

## 🎉 Enjoy Your Gesture Control System!

You now have a complete gesture-controlled system with:
- ✅ Real hardware control capability
- ✅ Simulation for testing without hardware
- ✅ Comprehensive documentation
- ✅ Easy setup with quick start scripts
- ✅ Extensible codebase for future enhancements

**Start with the simulation, test your gestures, then deploy to real hardware!**
