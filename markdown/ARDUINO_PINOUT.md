# Arduino Pinout Quick Reference

## Pin Configuration

| Component | Arduino Pin | Pin Type | Description |
|-----------|-------------|----------|-------------|
| **LED** | Pin 9 | Digital PWM | Controls LED brightness (PWM duty cycle) |
| **Servo Motor** | Pin 10 | Digital PWM | Controls servo speed (continuous rotation) |
| **LED Ground** | GND | Ground | Common ground for LED |
| **Servo Power** | 5V | Power | 5V power supply for servo (or external) |
| **Servo Ground** | GND | Ground | Common ground for servo |

## Arduino Uno Pin Layout

```
                    Arduino Uno
         ┌───────────────────────────┐
         │                           │
         │  [ ]  [ ]  [ ]  [ ]  [ ]  │  Digital 0-4
         │                           │
         │  [ ]  [ ]  [ ]  [9]  [10] │  Digital 5-10 (PWM: ~3,~5,~6,~9,~10,~11)
         │                           │
         │  [ ]  [ ]  [ ]            │  Digital 11-13
         │                           │
         │  [GND] [5V] ...           │  Power pins
         └───────────────────────────┘
                  │    │
                  │    └─── To Servo Red Wire (Power)
                  └──────── To LED Cathode & Servo Brown Wire (Ground)
```

## Wiring Color Code

### Standard LED
- **Long Leg (Anode +)**: Connects to resistor → Pin 9
- **Short Leg (Cathode -)**: Connects to GND

### Standard Servo Motor Colors
- **Orange/Yellow**: Signal wire → Pin 10
- **Red**: Power wire → 5V (or external 5V supply)
- **Brown/Black**: Ground wire → GND

## Complete Wiring Diagram

```
Arduino Uno Board
┌────────────────────────────────────────┐
│                                        │
│  Digital Pin 9 [~PWM]                  │───┐
│                                        │   │
│  Digital Pin 10 [~PWM]                 │───┼───┐
│                                        │   │   │
│  5V                                    │───┼───┼───┐
│                                        │   │   │   │
│  GND                                   │───┼───┼───┼───┐
│                                        │   │   │   │   │
└────────────────────────────────────────┘   │   │   │   │
                                             │   │   │   │
                         220Ω Resistor       │   │   │   │
                         ┌────────┐          │   │   │   │
                         │        │          │   │   │   │
LED (+) ─────────────────┴────────┴──────────┘   │   │   │
LED (-) ─────────────────────────────────────────┼───┘   │
                                                 │       │
Servo Signal (Orange) ───────────────────────────┘       │
Servo Power (Red) ───────────────────────────────────────┘
Servo Ground (Brown) ────────────────────────────────────┘
```

## Physical Connection Steps

### LED Connection
1. Place 220Ω resistor on breadboard
2. Connect one end of resistor to Arduino **Pin 9**
3. Connect other end of resistor to LED **Anode (+, long leg)**
4. Connect LED **Cathode (-, short leg)** to Arduino **GND**

### Servo Connection
1. Locate servo's 3 wires (Orange/Yellow, Red, Brown/Black)
2. Connect **Orange/Yellow** (signal) to Arduino **Pin 10**
3. Connect **Red** (power) to Arduino **5V** or external 5V supply
4. Connect **Brown/Black** (ground) to Arduino **GND**

### ⚠️ Important Notes
- Both LED and Servo grounds must connect to Arduino GND
- If using external power for servo, connect external GND to Arduino GND
- Pin 9 and Pin 10 are PWM-enabled pins (marked with ~ on board)
- Never reverse LED polarity (will not work, may damage LED)
- Servo can draw significant current; external 5V recommended for reliable operation

## PWM Pin Availability

Arduino Uno PWM pins (can be used for this project):
- Pin 3 (~)
- Pin 5 (~)
- Pin 6 (~)
- **Pin 9 (~)** ← Used for LED
- **Pin 10 (~)** ← Used for Servo
- Pin 11 (~)

To change pins, edit `gesture_control_arduino.ino`:
```cpp
const int LED_PIN = 9;     // Change to any PWM pin
const int SERVO_PIN = 10;  // Change to any PWM pin
```

## Breadboard Layout Example

```
Breadboard Layout (Top View)
═══════════════════════════════════════
  + Rail (Red)     - Rail (Blue)
───────────────────────────────────────
   5V ═══════╗      GND ═══════╗
             ║                 ║
   ╔═════════╝      ╔══════════╝
   ║ Servo Red      ║ Servo Brown
   ║                ║ LED Cathode
   
   Pin 10 ─────── Servo Orange
   
   Pin 9 ──┬── [220Ω] ──┬── LED Anode
           └────────────┘
```

## Testing Individual Components

### Test LED Only
1. Upload Arduino code
2. Open Serial Monitor (115200 baud)
3. Send commands:
   ```
   MODE:LED
   LED:ON
   LED:UP
   ```
4. LED should light up and get brighter

### Test Servo Only
1. Upload Arduino code
2. Open Serial Monitor (115200 baud)
3. Send commands:
   ```
   MODE:MOTOR
   MOTOR:ON
   MOTOR:UP
   ```
4. Servo should start rotating

## Power Requirements

| Component | Voltage | Current | Notes |
|-----------|---------|---------|-------|
| Arduino | 5V | ~50-100mA | Via USB or external |
| LED | ~2V | ~20mA | Through 220Ω resistor |
| Servo | 4.8-6V | 100-500mA | May need external power |

**Total System Current:**
- Arduino + LED only: ~120mA (USB safe)
- Arduino + LED + Servo: 200-600mA (external power recommended)

### External Power Options
1. **5V USB Power Bank**: Connect to Arduino Vin and GND
2. **5V Wall Adapter**: Connect to Arduino barrel jack (if available)
3. **Battery Pack**: 4x AA batteries (6V) or 5V regulated power supply

## Serial Communication Protocol

### Baud Rate
- **115200 bps** (bits per second)

### Command Format
```
MODE:LED       - Switch to LED control
MODE:MOTOR     - Switch to Motor control
LED:ON         - Turn LED on
LED:OFF        - Turn LED off
LED:UP         - Increase LED brightness
LED:DOWN       - Decrease LED brightness
MOTOR:ON       - Turn motor on
MOTOR:OFF      - Turn motor off
MOTOR:UP       - Increase motor speed
MOTOR:DOWN     - Decrease motor speed
STATUS         - Request status update
```

### Response Format
```
READY:Arduino Gesture Control System
MODE:LED
LED:ON
LED:LEVEL:3
MOTOR:OFF
MOTOR:LEVEL:0
STATUS:LED,ON,3,OFF,0
```

## Troubleshooting Quick Checks

### LED Not Working
- [ ] Check LED polarity (long leg = +)
- [ ] Verify 220Ω resistor present
- [ ] Check Pin 9 connection
- [ ] Test with multimeter (should see ~3-5V)

### Servo Not Working
- [ ] Check servo type (needs continuous rotation)
- [ ] Verify Pin 10 connection (signal wire)
- [ ] Check 5V power connection (red wire)
- [ ] Confirm GND connection (brown/black wire)
- [ ] Try external 5V power supply
- [ ] Test with Serial Monitor commands

### No Serial Communication
- [ ] Check USB cable (data cable, not charge-only)
- [ ] Verify correct COM port selected
- [ ] Confirm 115200 baud rate
- [ ] Close other programs using serial port
- [ ] Restart Arduino (unplug/replug USB)

## Safety Checklist

✓ **Before Powering On:**
- [ ] All connections secure
- [ ] No short circuits
- [ ] LED polarity correct
- [ ] Resistor in LED circuit
- [ ] Servo wires correct (signal, power, ground)
- [ ] External power voltage correct (if used)

✓ **During Operation:**
- [ ] Components not overheating
- [ ] Servo not stalling or obstructed
- [ ] LED brightness appropriate
- [ ] No loose wires
- [ ] Adequate power supply

## Additional Resources

- **Full Setup Guide**: See `ARDUINO_SETUP.md`
- **Gesture Controls**: See `README_SYSTEM.md`
- **Troubleshooting**: See `ARDUINO_SETUP.md` troubleshooting section
- **Arduino Reference**: https://www.arduino.cc/reference/en/

---

**Quick Start**: Connect LED to Pin 9 (with resistor), Servo to Pin 10, upload code, run `quick_start.bat`, select Arduino Client!
