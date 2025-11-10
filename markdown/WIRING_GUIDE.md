# Hardware Wiring Guide

## Component List

### Required Components:
1. Raspberry Pi 5
2. Raspberry Pi Camera Module (v2 or v3)
3. LED (any color, 5mm or 3mm)
4. 220Ω Resistor (for LED)
5. SG90 Servo Motor
6. Breadboard
7. Jumper wires (Male-to-Female and Male-to-Male)
8. (Optional) External 5V power supply for servo

---

## Camera Connection

**Raspberry Pi Camera Module**
- Connect ribbon cable to CSI camera port on Raspberry Pi 5
- Blue side faces USB ports, metal contacts face HDMI
- Gently lift black plastic clip, insert cable, push clip down

---

## LED Wiring

### GPIO Pin: 18 (Physical Pin 12)

```
Raspberry Pi GPIO 18 (Pin 12)
         |
         |
      [LED Anode] ----+
     (Long Leg, +)    |
                      |
                 [220Ω Resistor]
                      |
                      |
      [LED Cathode] --+
     (Short Leg, -)
         |
         |
    GND (Any Ground Pin)
```

### Step-by-Step:
1. Insert LED into breadboard
2. Connect 220Ω resistor to LED cathode (short leg)
3. Connect GPIO 18 (Physical Pin 12) to LED anode (long leg) with jumper wire
4. Connect other end of resistor to any GND pin with jumper wire

### Physical Pin Locations:
- **GPIO 18**: Physical Pin 12 (Row 6 right side)
- **GND Options**: Pins 6, 9, 14, 20, 25, 30, 34, 39

---

## Servo Motor (SG90 / Continuous Rotation) Wiring

### GPIO Pin: 13 (Physical Pin 33)

**IMPORTANT**: This system uses a **continuous rotation servo**, not a standard positional servo.

```
Continuous Rotation Servo:
  ┌─────────────┐
  │   [●]       │  ← Servo Body
  └─────────────┘
       |||
       |||
    ┌──┼┼┼──┐
    │  |||  │
    
Orange/Yellow Wire  → Signal (GPIO 13, Pin 33)
Red Wire           → Power (5V, Pin 2 or 4)
Brown/Black Wire   → Ground (GND, Pin 6)
```

### Continuous Rotation vs Standard Servo

**Standard Servo (SG90)**: Rotates to specific angles (0-180°)
**Continuous Rotation Servo**: Rotates continuously, speed is controlled

### Compatible Continuous Rotation Servos:
- FS90R (Feetech)
- SM-S4303R (SpringRC)
- Parallax Continuous Rotation Servo
- Modified SG90 (feedback pot removed)

### Converting Standard SG90 to Continuous Rotation:
If you only have a standard SG90, you can convert it:
1. Open the servo case
2. Remove or disable the feedback potentiometer
3. Remove the physical rotation stops
4. Reassemble

**OR simply use a continuous rotation servo for best results.**

### Step-by-Step:
1. **Signal Wire** (Orange/Yellow):
   - Connect to GPIO 13 (Physical Pin 33)

2. **Power Wire** (Red):
   - Connect to 5V (Physical Pin 2 or 4)
   - **Important**: For heavy loads or multiple servos, use external 5V power supply

3. **Ground Wire** (Brown/Black):
   - Connect to GND (Physical Pin 6, 9, 14, 20, 25, 30, 34, or 39)
   - Use same GND rail as LED for common ground

### Physical Pin Locations:
- **GPIO 13**: Physical Pin 33 (Row 17 left side)
- **5V Power**: Pin 2 or 4 (Top right corner, rows 1-2)
- **GND**: Pin 6, 9, 14, 20, 25, 30, 34, or 39

---

## Raspberry Pi 5 GPIO Pinout Reference

```
        3.3V [ 1] [ 2] 5V        
   GPIO 2    [ 3] [ 4] 5V        
   GPIO 3    [ 5] [ 6] GND       
   GPIO 4    [ 7] [ 8] GPIO 14   
         GND [ 9] [10] GPIO 15   
   GPIO 17   [11] [12] GPIO 18   ← LED SIGNAL
   GPIO 27   [13] [14] GND       
   GPIO 22   [15] [16] GPIO 23   
        3.3V [17] [18] GPIO 24   
   GPIO 10   [19] [20] GND       
   GPIO 9    [21] [22] GPIO 25   
   GPIO 11   [23] [24] GPIO 8    
         GND [25] [26] GPIO 7    
   GPIO 0    [27] [28] GPIO 1    
   GPIO 5    [29] [30] GND       
   GPIO 6    [31] [32] GPIO 12   
   GPIO 13   [33] [34] GND       ← SERVO SIGNAL
   GPIO 19   [35] [36] GPIO 16   
   GPIO 26   [37] [38] GPIO 20   
         GND [39] [40] GPIO 21   
```

---

## Complete Circuit Diagram (Text)

```
Raspberry Pi 5
┌─────────────────────────────────┐
│                                 │
│  Pin 2 (5V) ────────────┐      │
│                         │      │
│  Pin 12 (GPIO 18) ──┐   │      │
│                     │   │      │
│  Pin 33 (GPIO 13) ──┼───┼──┐   │
│                     │   │  │   │
│  Pin 6 (GND) ───────┼───┼──┼─┐ │
│                     │   │  │ │ │
└─────────────────────┼───┼──┼─┼─┘
                      │   │  │ │
                      │   │  │ │
                 ┌────┘   │  │ │
                 │        │  │ │
              [LED Anode] │  │ │
              (long leg)  │  │ │
                 │        │  │ │
           [220Ω Resistor]│  │ │
                 │        │  │ │
              [LED Cathode]  │ │
              (short leg) │  │ │
                 │        │  │ │
                 └────────┘  │ │
                             │ │
                       ┌─────┘ │
                       │       │
                 [SG90 Servo]  │
                    ┌─┴─┐      │
              Red ──┤ S │      │
          Orange/Yel│ E │──────┘
              Brown─┤ R │
                    │ V │──────┐
                    │ O │      │
                    └───┘      │
                             ──┴── GND
```

---

## Safety Checklist

Before powering on:
- [ ] LED has resistor in series (prevents burnout)
- [ ] LED polarity is correct (long leg to GPIO)
- [ ] Servo wires match: Orange→GPIO, Red→5V, Brown→GND
- [ ] All ground connections share common ground
- [ ] No short circuits (wires not touching)
- [ ] Camera ribbon cable properly seated

---

## Testing Individual Components

### Test LED:
```bash
# After running gesture_control_system.py
# Show "1" gesture to switch to LED mode
# Show open hand to turn on
# Show thumbs up/down to adjust brightness
```

### Test Servo:
```bash
# After running gesture_control_system.py
# Show "2" gesture to switch to Motor mode
# Show open hand to turn on
# Show thumbs up/down to adjust angle
```

### Quick Hardware Test (Python):
```python
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

# Test LED
GPIO.setup(18, GPIO.OUT)
led_pwm = GPIO.PWM(18, 1000)
led_pwm.start(50)  # 50% brightness
time.sleep(2)
led_pwm.stop()

# Test Servo
GPIO.setup(13, GPIO.OUT)
servo_pwm = GPIO.PWM(13, 50)
servo_pwm.start(7.5)  # 90 degrees
time.sleep(2)
servo_pwm.stop()

GPIO.cleanup()
print("Test complete!")
```

---

## Troubleshooting

### LED Issues:
- **Not lighting**: Check polarity, try reversing LED
- **Too dim**: Check resistor value (use 220Ω or lower)
- **Not responding**: Verify GPIO 18 connection

### Servo Issues:
- **Jittering**: Use external 5V power supply
- **Not moving**: Check all three wires connected
- **Erratic behavior**: Add 100µF capacitor across power pins

### GPIO Errors:
- **Permission denied**: Run with `sudo` or add user to gpio group
- **Pin already in use**: Run `GPIO.cleanup()` or reboot

---

## Advanced: External Power for Servo

For more reliable servo operation:

```
External 5V Power Supply (recommended for multiple servos)
┌────────┐
│  5V DC │
│ Supply │
└─┬──┬───┘
  │  │
  │  └─────────────┐
  │                │
  │           ┌────┴────┐
  │           │  Servo  │
  │           │  Red    │
  │           └─────────┘
  │
  └─── Connect to Raspberry Pi GND (common ground!)
```

**Important**: Always connect external power supply ground to Raspberry Pi ground!

---

## Need Help?

- Check connections match this guide exactly
- Verify GPIO pin numbers (BCM mode, not physical)
- Test components individually before full system
- Ensure camera is enabled: `sudo raspi-config`
- Check for loose wires on breadboard
