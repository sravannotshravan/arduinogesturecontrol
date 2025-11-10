# Gesture-Controlled LED and Servo Motor System

Complete gesture control system for Raspberry Pi 5 with LED and Servo Motor control using hand gestures detected via camera.

## 🎯 Features

- **6 Hand Gestures Detection**:
  - ☝ Number 1: Switch to LED control mode
  - ✌ Number 2: Switch to Motor control mode  
  - ✋ Open Hand: Turn device ON
  - ✊ Closed Hand: Turn device OFF
  - 👍 Thumbs Up (hold 2s): Increase brightness/speed
  - 👎 Thumbs Down (hold 2s): Decrease brightness/speed

- **PWM Control**:
  - LED: 5 brightness levels (0-100%)
  - Servo: 5 angle positions (0-180°)

- **3 Program Modes**:
  1. **gesture_control_system.py** - Real hardware control (Raspberry Pi only)
  2. **gesture_control_simulation.py** - Visual simulation (any computer)
  3. **gesture_testing.py** - Gesture detection testing (any computer)

## 🔌 Hardware Connections

### LED Connection
- **Pin**: GPIO 18 (Physical Pin 12)
- **Component**: LED with 220Ω resistor
- **Wiring**:
  - GPIO 18 → LED anode (long leg) → 220Ω resistor → LED cathode (short leg) → GND

### Servo Motor SG90 Connection
- **Pin**: GPIO 13 (Physical Pin 33)
- **Component**: SG90 Servo Motor (Continuous Rotation)
- **Wiring**:
  - Orange/Yellow wire → GPIO 13 (Physical Pin 33)
  - Red wire → 5V (Physical Pin 2 or 4)
  - Brown/Black wire → GND (Physical Pin 6, 9, 14, 20, 25, 30, 34, or 39)

**Note**: This system is designed for a **continuous rotation servo**. If you have a standard positional servo (SG90), you'll need to either:
- Convert it to continuous rotation (by removing the position feedback potentiometer), OR
- Use a continuous rotation servo like FS90R, SM-S4303R, or similar

### Camera
- Raspberry Pi Camera Module v2/v3 connected to camera port (CSI)

## 📦 Installation

### For Raspberry Pi 5 (Real Hardware)

1. **Enable Camera**:
```bash
sudo raspi-config
# Interface Options → Camera → Enable
```

2. **Update System**:
```bash
sudo apt update
sudo apt upgrade -y
```

3. **Install System Dependencies**:
```bash
sudo apt install -y python3-pip python3-opencv python3-venv
sudo apt install -y libatlas-base-dev libhdf5-dev libhdf5-serial-dev
sudo apt install -y libharfbuzz0b libwebp7 libtiff5 libjasper1
sudo apt install -y libilmbase25 libopenexr25 libgstreamer1.0-0
```

4. **Create Virtual Environment**:
```bash
cd "Gesture controlled LED and Motor"
python3 -m venv .venv
source .venv/bin/activate  # On Linux/Raspberry Pi
```

5. **Install Python Packages**:
```bash
pip install opencv-python mediapipe numpy RPi.GPIO
```

### For Windows/Mac (Simulation & Testing Only)

1. **Create Virtual Environment**:
```powershell
cd "Gesture controlled LED and Motor"
python -m venv .venv
.venv\Scripts\Activate.ps1  # PowerShell
# OR
.venv\Scripts\activate.bat  # CMD
```

2. **Install Python Packages** (excluding RPi.GPIO):
```powershell
pip install opencv-python mediapipe numpy
```

## 🚀 Usage

### On Raspberry Pi (Real Hardware Control)

```bash
source .venv/bin/activate
python gesture_control_system.py
```

**Controls**:
1. Show **1 finger** to switch to LED mode
2. Show **2 fingers** to switch to Motor mode
3. Show **open hand** to turn the current device ON
4. Show **closed fist** to turn the current device OFF
5. Hold **thumbs up** for 2 seconds to increase brightness/angle
6. Hold **thumbs down** for 2 seconds to decrease brightness/angle
7. Press **'q'** to quit

### On Any Computer (Simulation Mode)

```bash
# Windows
.venv\Scripts\Activate.ps1
python gesture_control_simulation.py

# Linux/Mac
source .venv/bin/activate
python gesture_control_simulation.py
```

This shows a visual simulation of the LED and servo motor alongside the camera feed. Perfect for testing without hardware!

### Gesture Testing (Any Computer)

```bash
# Windows
.venv\Scripts\Activate.ps1
python gesture_testing.py

# Linux/Mac
source .venv/bin/activate
python gesture_testing.py
```

Test gesture detection accuracy with:
- Real-time gesture recognition
- Detection statistics
- Finger count display
- Gesture hold time tracking
- Press **'r'** to reset statistics
- Press **'q'** to quit

## 🎮 How It Works

### Mode Selection
- **LED Mode** (Yellow border in simulation): Controls LED brightness
- **Motor Mode** (Orange border in simulation): Controls servo angle

### PWM Control Levels
Both devices have 5 control levels:

**LED Brightness**:
- Level 1: 20% brightness
- Level 2: 40% brightness
- Level 3: 60% brightness (default)
- Level 4: 80% brightness
- Level 5: 100% brightness

**Servo Rotation Speed**:
- Level 1: 20% speed (slow rotation)
- Level 2: 40% speed
- Level 3: 60% speed (default - medium rotation)
- Level 4: 80% speed (fast rotation)
- Level 5: 100% speed (maximum rotation speed)

The servo continuously rotates when ON, and the speed increases/decreases with the level.

### Gesture Hold Detection
Thumbs up/down require a 2-second hold to prevent accidental triggers:
- A countdown timer appears on screen
- The action executes after 2 seconds
- You can adjust levels multiple times by continuing to hold

## 📁 File Structure

```
Gesture controlled LED and Motor/
├── gesture_control_system.py      # Main program for Raspberry Pi
├── gesture_control_simulation.py  # Simulation mode (any computer)
├── gesture_testing.py             # Gesture detection testing
├── hand_gesture_detection.py      # Original detection demo
├── requirements.txt               # Python dependencies
└── README_SYSTEM.md              # This file
```

## 🔧 Troubleshooting

### Camera Issues
- **Error: Could not open camera**
  - Check camera connection to CSI port
  - Enable camera: `sudo raspi-config`
  - Test: `libcamera-hello`

### GPIO Permission Denied
- Run with sudo: `sudo python gesture_control_system.py`
- Or add user to gpio group: `sudo usermod -a -G gpio $USER`

### Servo Jittering
- Use external 5V power supply for servo (not from Pi)
- Add 100µF capacitor across servo power pins
- Ensure good ground connection

### LED Not Working
- Check polarity (long leg = anode = positive)
- Verify resistor value (220Ω recommended)
- Test LED with multimeter

### MediaPipe/OpenCV Import Errors
```bash
pip install --upgrade opencv-python mediapipe numpy
```

### Virtual Environment Issues on Windows
If you see path errors with spaces:
```powershell
# Use quotes around the path
& "C:\Users\srava\Documents\Gesture controlled LED and Motor\.venv\Scripts\python.exe" gesture_control_simulation.py

# Or navigate to the directory first
cd "C:\Users\srava\Documents\Gesture controlled LED and Motor"
.venv\Scripts\Activate.ps1
python gesture_control_simulation.py
```

## 🎯 Testing Workflow

1. **Start with `gesture_testing.py`** on any computer to verify your gestures are detected correctly
2. **Run `gesture_control_simulation.py`** to see how the system responds to your gestures
3. **Deploy to Raspberry Pi** with `gesture_control_system.py` for real hardware control

## 🔒 Safety Notes

- Servo motors can draw significant current - use external power if running multiple devices
- LEDs should always have current-limiting resistors
- Disconnect power when wiring
- Don't exceed GPIO current limits (16mA per pin, 50mA total)

## 📝 Customization

### Adjust Detection Sensitivity
Edit detection confidence in any .py file:
```python
self.hands = self.mp_hands.Hands(
    min_detection_confidence=0.7,  # Lower = easier detection
    min_tracking_confidence=0.5     # Lower = smoother tracking
)
```

### Change Hold Duration
Modify in main control section:
```python
HOLD_DURATION = 2.0  # Change to desired seconds
```

### Change GPIO Pins
In `gesture_control_system.py`:
```python
LED_PIN = 18    # Change to your preferred GPIO
SERVO_PIN = 13  # Change to your preferred GPIO
```

## 📜 License

Open source - feel free to modify and use for educational purposes.

## 🙏 Credits

- MediaPipe by Google for hand tracking
- OpenCV for computer vision
- RPi.GPIO for Raspberry Pi hardware control
