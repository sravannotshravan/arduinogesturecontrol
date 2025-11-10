# Arduino Setup Guide

## Hardware Requirements

1. **Arduino Board** (Uno, Nano, Mega, or compatible)
2. **LED** with 220Ω resistor
3. **Continuous Rotation Servo Motor** (e.g., FS90R, SM-S4303R, or modified SG90)
4. **USB Cable** (for connecting Arduino to laptop)
5. **Breadboard and jumper wires** (optional but recommended)
6. **External Power Supply** (5V, 1-2A) for servo motor (recommended)

## Arduino Pinout

```
Arduino Board
┌─────────────────┐
│                 │
│  Digital Pin 9  ├──────→ LED (through 220Ω resistor)
│                 │
│  Digital Pin 10 ├──────→ Servo Signal Wire (Orange/Yellow)
│                 │
│  5V             ├──────→ Servo Power Wire (Red)
│                 │
│  GND            ├──────→ LED Cathode (-) & Servo Ground (Brown/Black)
│                 │
└─────────────────┘
```

## Wiring Instructions

### LED Connection
1. Connect **Arduino Pin 9** → **220Ω Resistor** → **LED Anode (+, longer leg)**
2. Connect **LED Cathode (-, shorter leg)** → **Arduino GND**

### Servo Motor Connection
1. **Signal Wire** (Orange/Yellow) → **Arduino Pin 10**
2. **Power Wire** (Red) → **5V** (use external power supply if available)
3. **Ground Wire** (Brown/Black) → **Arduino GND**

⚠️ **Important Notes:**
- **Pin 9** and **Pin 10** are PWM-capable pins required for this project
- For continuous rotation servo, use a servo specifically designed for it (FS90R, SM-S4303R) or modify a standard servo
- If servo draws too much current, use an external 5V power supply
- Always connect grounds together (Arduino GND, LED GND, Servo GND, External Power GND)

## Wiring Diagram

```
        ┌──────────────────────────────────────┐
        │         Arduino Board                │
        │                                      │
Pin 9 ──┤                                      │
        │                                      │
Pin 10 ─┤                                      │
        │                                      │
5V ─────┤                                      │
        │                                      │
GND ────┤                                      │
        └──────────────────────────────────────┘
          │          │         │
          │          │         └─────┐
          │          │               │
          ▼          ▼               ▼
       [Resistor] [Servo]          [GND]
          │          │ │ │
          ▼          │ │ │
        [LED]        │ │ │
          │          │ │ │
          └──────────┘ │ │
                       │ │
              Signal ──┘ │
              Power ─────┘
```

## Software Setup

### Step 1: Install Arduino IDE
1. Download from: https://www.arduino.cc/en/software
2. Install for your operating system
3. Launch Arduino IDE

### Step 2: Upload Arduino Code
1. Open `gesture_control_arduino/gesture_control_arduino.ino` in Arduino IDE
2. Connect Arduino to laptop via USB
3. Select **Tools > Board** → Choose your Arduino board (e.g., Arduino Uno)
4. Select **Tools > Port** → Choose the COM port (e.g., COM3)
5. Click **Upload** button (→) or press Ctrl+U
6. Wait for "Done uploading" message
7. Check that Arduino LED blinks during upload

### Step 3: Install Python Dependencies
1. Open Command Prompt or PowerShell
2. Navigate to project folder:
   ```powershell
   cd "c:\Users\srava\Documents\Gesture controlled LED and Motor"
   ```
3. Activate virtual environment:
   ```powershell
   .venv\Scripts\activate
   ```
4. Install pyserial:
   ```powershell
   pip install pyserial
   ```

### Step 4: Verify Connection
1. In Arduino IDE, open **Tools > Serial Monitor**
2. Set baud rate to **115200**
3. You should see:
   ```
   Gesture Control System v1.0
   Initializing...
   Servo attached to pin 10
   Ready!
   READY:Arduino Gesture Control System
   ```
4. Close Serial Monitor before running Python client

## Running the System

### Using Quick Start Script (Recommended)
1. Double-click `quick_start.bat`
2. Wait for setup to complete
3. Select option **1** (Arduino Client)
4. Follow checklist prompts
5. System will auto-detect Arduino and start

### Manual Execution
1. Open Command Prompt in project folder
2. Activate virtual environment:
   ```powershell
   .venv\Scripts\activate
   ```
3. Run client:
   ```powershell
   python gesture_control_client_arduino.py
   ```
4. Select COM port if prompted

## How to Use

### Gesture Controls

| Gesture | Action | Description |
|---------|--------|-------------|
| ☝ **1 Finger** | Switch to LED Mode | Control LED brightness |
| ✌ **2 Fingers** | Switch to Motor Mode | Control servo speed |
| ✋ **Open Hand** | Turn ON | Activate current device |
| ✊ **Closed Fist** | Turn OFF | Deactivate current device |
| 👍 **Thumbs Up** (hold 2s) | Increase | Brightness/Speed up |
| 👎 **Thumbs Down** (hold 2s) | Decrease | Brightness/Speed down |

### Control Levels

**LED Brightness:**
- Level 0: OFF
- Level 1: 20% brightness
- Level 2: 40% brightness
- Level 3: 60% brightness
- Level 4: 80% brightness
- Level 5: 100% brightness (full)

**Servo Motor Speed:**
- Level 0: STOPPED
- Level 1: Slow rotation
- Level 2: Medium-slow rotation
- Level 3: Medium rotation
- Level 4: Medium-fast rotation
- Level 5: Fast rotation

### On-Screen Display
- **MODE**: Shows current control mode (LED or MOTOR)
- **Status Line**: Shows device state (ON/OFF) and level (1-5)
- **Gesture Label**: Shows detected gesture in green
- **Hand Skeleton**: Visual feedback of hand detection

### Tips for Best Results
1. **Lighting**: Use good lighting for better hand detection
2. **Background**: Plain, contrasting background works best
3. **Distance**: Keep hand 30-60cm from camera
4. **Gestures**: Make gestures clear and distinct
5. **Hold Time**: For thumbs up/down, hold steady for 2 seconds
6. **Mode Switching**: Switch mode before adjusting device

## Troubleshooting

### Arduino Not Detected
- Check USB cable connection
- Install CH340/CH341 drivers if using clone Arduino
- Try different USB port
- Check Device Manager for COM port

### Serial Communication Errors
- Close Arduino IDE Serial Monitor
- Close other programs using COM port
- Restart Arduino (unplug/replug USB)
- Check baud rate is 115200

### Camera Not Working
- Check camera permissions in Windows Settings
- Close other apps using camera (Zoom, Teams, etc.)
- Try different camera (use index 1: `cv2.VideoCapture(1)`)

### Gesture Detection Issues
- Improve lighting conditions
- Remove background clutter
- Keep only one hand in frame
- Make gestures more distinct
- See `GESTURE_TIPS.md` for detailed guidance

### LED Not Lighting
- Check LED polarity (long leg to positive)
- Verify resistor value (220Ω)
- Check Pin 9 connection
- Test with Serial Monitor commands: `LED:ON`

### Servo Not Moving
- Check servo power supply (may need external 5V)
- Verify servo is continuous rotation type
- Check Pin 10 connection
- Test with Serial Monitor commands: `MOTOR:ON` then `MOTOR:UP`
- Measure voltage at servo power wire (should be ~5V)

### Serial Monitor Testing
You can test Arduino without Python by sending commands in Serial Monitor:
```
MODE:LED          // Switch to LED control
LED:ON            // Turn LED on
LED:UP            // Increase brightness
LED:DOWN          // Decrease brightness
LED:OFF           // Turn LED off

MODE:MOTOR        // Switch to Motor control
MOTOR:ON          // Turn motor on
MOTOR:UP          // Increase speed
MOTOR:DOWN        // Decrease speed
MOTOR:OFF         // Turn motor off

STATUS            // Get current status
```

## Advanced Configuration

### Change Pins
Edit `gesture_control_arduino.ino`:
```cpp
const int LED_PIN = 9;     // Change to your LED pin
const int SERVO_PIN = 10;  // Change to your servo pin
```
Must be PWM-capable pins (3, 5, 6, 9, 10, 11 on Uno)

### Change Baud Rate
1. In Arduino code, change:
   ```cpp
   Serial.begin(115200);  // Change to desired rate
   ```
2. In Python code, change:
   ```python
   baudrate=115200  // Match Arduino rate
   ```

### Adjust LED Brightness Levels
Edit Arduino code `ledLevels` array:
```cpp
const int ledLevels[6] = {0, 51, 102, 153, 204, 255};
// Values: 0 (off), 51 (20%), 102 (40%), 153 (60%), 204 (80%), 255 (100%)
```

### Adjust Servo Speed Levels
Edit Arduino code:
```cpp
// In setMotorLevel() function
case 1: motorServo.write(100); break;  // Slowest
case 2: motorServo.write(120); break;
case 3: motorServo.write(140); break;
case 4: motorServo.write(160); break;
case 5: motorServo.write(180); break;  // Fastest
```
Range: 90 (stop), <90 (reverse), >90 (forward) for continuous rotation servos

## Safety Notes

⚠️ **Electrical Safety:**
- Never connect servo directly to Arduino 5V pin if it draws >500mA
- Use proper resistor for LED (220Ω for 5V)
- Don't short circuit pins
- Disconnect power when wiring

⚠️ **Servo Safety:**
- Continuous rotation servos can spin indefinitely
- Make sure nothing obstructs servo movement
- Don't force servo mechanically
- Use appropriate power supply for servo current requirements

## Next Steps

1. **Test Basic Detection**: Run `gesture_testing.py` to verify hand detection
2. **Test Simulation**: Run `gesture_control_simulation.py` to see visual feedback
3. **Connect Hardware**: Wire LED and servo as shown above
4. **Upload Arduino Code**: Use Arduino IDE to upload sketch
5. **Run System**: Use `quick_start.bat` and select Arduino Client
6. **Calibrate Gestures**: Adjust hand position and lighting as needed

## Additional Resources

- **Full Documentation**: See `README_SYSTEM.md`
- **Gesture Tips**: See `GESTURE_TIPS.md`
- **Project Summary**: See `PROJECT_SUMMARY.md`
- **Arduino Reference**: https://www.arduino.cc/reference/en/
- **MediaPipe Hands**: https://google.github.io/mediapipe/solutions/hands.html

---

**Project Version**: 2.0 (Arduino USB Serial)
**Last Updated**: 2024
