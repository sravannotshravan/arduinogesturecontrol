# 🎮 Gesture Control System - Arduino Version

## ✨ What You Have Now

A complete gesture-controlled system that lets you control an LED and continuous rotation servo motor using hand gestures detected by your laptop's webcam!

## 📁 Project Files

### Arduino Code
- **`gesture_control_arduino/gesture_control_arduino.ino`** - Upload this to your Arduino

### Laptop Code (Python)
- **`gesture_control_client_arduino.py`** - Main program (connects laptop to Arduino via USB)
- **`gesture_control_simulation.py`** - Visual simulation (no hardware needed)
- **`gesture_testing.py`** - Test gesture detection only

### Documentation
- **`ARDUINO_SETUP.md`** - Complete setup guide (START HERE!)
- **`ARDUINO_PINOUT.md`** - Wiring diagrams and pin reference
- **`README_SYSTEM.md`** - Full system documentation
- **`GESTURE_TIPS.md`** - Tips for better gesture detection
- **`quick_start.bat`** - Windows quick start script

### Configuration
- **`requirements.txt`** - Python package dependencies

## 🔌 Hardware Setup (Quick Version)

### What You Need
1. Arduino board (Uno/Nano/Mega)
2. LED + 220Ω resistor
3. Continuous rotation servo motor (FS90R, SM-S4303R, or modified SG90)
4. USB cable
5. Breadboard and jumper wires
6. Optional: External 5V power supply for servo

### Wiring
```
Arduino Pin 9  → 220Ω Resistor → LED (+)
LED (-)        → Arduino GND

Arduino Pin 10 → Servo Signal Wire (Orange)
Arduino 5V     → Servo Power Wire (Red)
Arduino GND    → Servo Ground Wire (Brown)
```

**Visual Pinout:**
```
┌─────────────────┐
│  Arduino Uno    │
│                 │
│  Pin 9  [~PWM]  ├──→ LED (with resistor)
│  Pin 10 [~PWM]  ├──→ Servo Signal
│  5V             ├──→ Servo Power
│  GND            ├──→ LED Ground & Servo Ground
└─────────────────┘
```

## 💻 Software Setup (Quick Version)

### Step 1: Arduino IDE
1. Download from https://www.arduino.cc/en/software
2. Open `gesture_control_arduino/gesture_control_arduino.ino`
3. Select your board: Tools > Board > Arduino Uno (or your model)
4. Select COM port: Tools > Port > COM3 (or your port)
5. Click Upload button (→)
6. Wait for "Done uploading"

### Step 2: Python Setup
Open PowerShell in project folder:
```powershell
# Navigate to project folder
cd "c:\Users\srava\Documents\Gesture controlled LED and Motor"

# Activate virtual environment
.venv\Scripts\activate

# Install required package
pip install pyserial
```

## 🚀 How to Run

### Option 1: Quick Start Script (Easiest)
1. Double-click **`quick_start.bat`**
2. Wait for setup
3. Select **1** (Arduino Client)
4. Ensure Arduino is connected
5. Start using gestures!

### Option 2: Manual
```powershell
cd "c:\Users\srava\Documents\Gesture controlled LED and Motor"
.venv\Scripts\activate
python gesture_control_client_arduino.py
```

## 🤚 Gesture Controls

| Gesture | Function | What It Does |
|---------|----------|--------------|
| ☝ **1 Finger** | Mode: LED | Switch to LED brightness control |
| ✌ **2 Fingers** | Mode: Motor | Switch to motor speed control |
| ✋ **Open Hand** | Turn ON | Activate current device |
| ✊ **Closed Fist** | Turn OFF | Deactivate current device |
| 👍 **Thumbs Up** (hold 2s) | Increase | Brightness ↑ or Speed ↑ |
| 👎 **Thumbs Down** (hold 2s) | Decrease | Brightness ↓ or Speed ↓ |

### Control Levels
- **LED**: 5 brightness levels (20%, 40%, 60%, 80%, 100%)
- **Motor**: 5 speed levels (slow → fast continuous rotation)

## 🎬 Typical Usage Flow

1. **Start the program** (use `quick_start.bat`)
2. **Show 1 finger** (switch to LED mode)
3. **Open hand** (turn LED on at level 3)
4. **Thumbs up** for 2 seconds (increase brightness to level 4)
5. **Show 2 fingers** (switch to motor mode)
6. **Open hand** (turn motor on at level 3)
7. **Thumbs up** for 2 seconds (increase speed to level 4)
8. **Closed fist** (turn motor off)
9. Press **'q'** to quit

## 🔍 On-Screen Display

When running, you'll see:
- **Hand skeleton overlay** (green lines showing hand landmarks)
- **Current gesture label** (e.g., "ONE", "OPEN", "THUMBS_UP")
- **Mode indicator** (LED or MOTOR in colored text)
- **Device status** (ON/OFF and level 1-5)

## 📡 Serial Communication Protocol

The laptop and Arduino communicate via USB serial at **115200 baud**.

### Commands Sent (Laptop → Arduino)
```
MODE:LED        - Switch to LED control
MODE:MOTOR      - Switch to Motor control
LED:ON          - Turn LED on
LED:OFF         - Turn LED off
LED:UP          - Increase brightness
LED:DOWN        - Decrease brightness
MOTOR:ON        - Turn motor on
MOTOR:OFF       - Turn motor off
MOTOR:UP        - Increase speed
MOTOR:DOWN      - Decrease speed
STATUS          - Request status
```

### Responses Received (Arduino → Laptop)
```
READY:Arduino Gesture Control System
MODE:LED
LED:ON
LED:LEVEL:3
MOTOR:OFF
STATUS:LED,ON,3,OFF,0
```

## 🛠️ Testing Without Python

You can test Arduino directly using Serial Monitor:

1. Open Arduino IDE
2. Tools > Serial Monitor
3. Set baud rate to **115200**
4. Type commands:
   ```
   MODE:LED
   LED:ON
   LED:UP
   LED:DOWN
   LED:OFF
   ```

## 🔧 Troubleshooting

### Arduino not detected
- Check USB cable (must be data cable, not charge-only)
- Install CH340 drivers if using clone Arduino
- Try different USB port
- Check Device Manager for COM port

### Camera not working
- Close other apps using camera (Zoom, Teams, etc.)
- Check camera permissions in Windows Settings
- Try different camera index if multiple cameras

### Gesture detection issues
- Improve lighting (bright, even light)
- Use plain background
- Keep hand 30-60cm from camera
- Make gestures clear and distinct
- See `GESTURE_TIPS.md`

### LED not lighting
- Check LED polarity (long leg = +)
- Verify 220Ω resistor
- Test with Serial Monitor: `LED:ON`
- Check Pin 9 connection

### Servo not moving
- Verify continuous rotation servo type
- Use external 5V power supply
- Check Pin 10 connection
- Test with Serial Monitor: `MOTOR:ON` then `MOTOR:UP`

## 📚 Documentation Quick Links

| Document | Purpose |
|----------|---------|
| `ARDUINO_SETUP.md` | **Complete setup guide** - start here! |
| `ARDUINO_PINOUT.md` | Detailed wiring and pinout diagrams |
| `README_SYSTEM.md` | Full system documentation |
| `GESTURE_TIPS.md` | Improve gesture detection accuracy |
| `PROJECT_SUMMARY.md` | Technical project overview |

## 🎯 Quick Start Checklist

Setup:
- [ ] Arduino IDE installed
- [ ] Arduino code uploaded (`gesture_control_arduino.ino`)
- [ ] LED wired to Pin 9 with resistor
- [ ] Servo wired to Pin 10
- [ ] Python environment activated
- [ ] pyserial installed (`pip install pyserial`)

Run:
- [ ] Arduino connected via USB
- [ ] Run `quick_start.bat` or `python gesture_control_client_arduino.py`
- [ ] Select correct COM port
- [ ] Camera feed appears
- [ ] Test gestures!

## 💡 Tips for Success

### Hardware
- Use PWM pins (Pin 9 and 10 on Arduino Uno)
- External 5V power recommended for servo
- Continuous rotation servo required (not standard angle servo)
- Always connect grounds together

### Software
- Close Serial Monitor before running Python client
- Only one program can use serial port at a time
- Baud rate must match: 115200

### Gesture Detection
- Good lighting is critical
- Plain background helps
- One hand in frame
- Hold thumbs up/down steady for 2 seconds
- Switch mode before adjusting device

## 🎨 What Makes This Special

✅ **No Raspberry Pi needed** - Works with any laptop + Arduino
✅ **Simple wiring** - Just 2 components (LED + servo)
✅ **USB communication** - No WiFi or networking setup
✅ **Visual feedback** - See exactly what's detected
✅ **Intuitive gestures** - Natural hand movements
✅ **Adjustable levels** - 5 levels of control for each device
✅ **Mode switching** - Control multiple devices with same gestures
✅ **Real-time response** - Instant feedback
✅ **Simulation mode** - Test without hardware
✅ **Testing mode** - Verify gesture detection

## 🚀 Next Steps

1. **Follow full setup**: Read `ARDUINO_SETUP.md` carefully
2. **Wire hardware**: Use `ARDUINO_PINOUT.md` as reference
3. **Upload Arduino code**: Use Arduino IDE
4. **Install Python packages**: `pip install pyserial`
5. **Run quick start**: Double-click `quick_start.bat`
6. **Test gestures**: Start with simulation mode first
7. **Connect hardware**: Run Arduino client
8. **Enjoy!** Control LED and motor with hand gestures

## 📞 Need Help?

1. Check `ARDUINO_SETUP.md` troubleshooting section
2. Verify wiring with `ARDUINO_PINOUT.md`
3. Test gesture detection with `gesture_testing.py`
4. Try simulation mode: `python gesture_control_simulation.py`
5. Check Serial Monitor for Arduino messages

---

## 🎉 You're All Set!

Everything you need is ready:
- ✅ Arduino firmware written
- ✅ Python client created
- ✅ Batch script updated
- ✅ Complete documentation provided
- ✅ Wiring diagrams included
- ✅ Testing tools available

**Just follow `ARDUINO_SETUP.md` and you'll be controlling devices with hand gestures in minutes!**

---

**Project**: Gesture Controlled LED and Motor (Arduino Version)
**Platform**: Windows + Arduino
**Communication**: USB Serial (115200 baud)
**Languages**: C++ (Arduino), Python 3.8+ (Laptop)
**Dependencies**: OpenCV, MediaPipe, pyserial
