# 🔄 Continuous Rotation Servo Guide

## Understanding Servo Types

### Standard Positional Servo (SG90)
- Rotates to specific angles (0° to 180°)
- Used for: Robot arms, camera gimbals, RC car steering
- **NOT suitable for this project as-is**

### Continuous Rotation Servo
- Rotates continuously like a DC motor
- Speed and direction controlled by PWM signal
- Used for: Wheels, fans, conveyor belts, continuous motion
- **Required for this project**

---

## 🛒 Recommended Continuous Rotation Servos

### 1. FS90R (Feetech) - Recommended ⭐
- **Price**: ~$8-12 USD
- **Specs**: 1.5kg·cm torque, 130RPM at 6V
- **Pros**: Direct replacement for SG90, widely available
- **Where**: Amazon, AliExpress, robotics suppliers

### 2. SM-S4303R (SpringRC)
- **Price**: ~$7-10 USD
- **Specs**: 3.5kg·cm torque, 50RPM at 5V
- **Pros**: Higher torque, affordable
- **Where**: Amazon, eBay

### 3. Parallax Continuous Rotation Servo
- **Price**: ~$15 USD
- **Specs**: High quality, 50RPM
- **Pros**: Excellent documentation, reliable
- **Where**: Parallax website, SparkFun

### 4. TowerPro MG90D (Metal Gear)
- **Price**: ~$10-15 USD
- **Specs**: Metal gears, 10kg·cm torque
- **Pros**: Very durable, high torque
- **Where**: Amazon, hobby stores

---

## 🔧 Converting Standard SG90 to Continuous Rotation

If you only have a standard SG90 servo, you can convert it:

### Required Tools:
- Small Phillips screwdriver
- Wire cutters or pliers
- Optional: Multimeter

### Conversion Steps:

1. **Open the Servo**
   - Remove the 4 screws on the bottom
   - Carefully separate the two halves
   - Note the gear arrangement

2. **Remove the Potentiometer**
   - The potentiometer (variable resistor) provides position feedback
   - Cut the wires to the potentiometer OR
   - Desolder it from the circuit board

3. **Set Potentiometer to Center**
   - Using a multimeter, find the center position
   - OR manually set it to middle position (~2.5V)
   - Alternatively, replace with fixed resistors (2.2kΩ each)

4. **Remove Physical Stops**
   - The main output gear has a small plastic tab
   - Carefully cut or file off this tab
   - This allows 360° rotation

5. **Reassemble**
   - Put gears back in order
   - Close the case
   - Screw it back together

6. **Test**
   - Connect to Raspberry Pi
   - Send neutral signal (7.5% duty cycle)
   - Servo should stop
   - Adjust if needed

### Wiring After Conversion:
```
Wire Color    Function
─────────────────────────
Orange/Yellow Signal (to GPIO 13)
Red          5V Power
Brown/Black  Ground
```

### Calibration:
The converted servo may not stop perfectly at 7.5% duty cycle. You may need to adjust the "neutral" value in the code:

```python
# In gesture_control_system.py, around line 198
# Adjust this value if motor doesn't stop at neutral
base_stop = 7.5  # Try 7.0-8.0 if needed
```

---

## 🔌 Wiring Continuous Rotation Servo

### Pin Connections (Same as Standard Servo):

```
Raspberry Pi 5          Continuous Rotation Servo
─────────────────────   ─────────────────────────
GPIO 13 (Pin 33)    →   Signal Wire (Orange/Yellow)
5V (Pin 2 or 4)     →   Power Wire (Red)
GND (Pin 6)         →   Ground Wire (Brown/Black)
```

### Physical Layout:
```
Raspberry Pi GPIO Header (Top View):
┌─────────────────────────────────┐
│  3.3V [1] [2] 5V ← Connect Red  │
│       [3] [4] 5V                │
│       [5] [6] GND ← Connect Brn │
│       ...                       │
│       [31][32]                  │
│  GPIO13[33][34] GND             │
│       [35][36]                  │
│       [37][38]                  │
│       [39][40]                  │
└─────────────────────────────────┘
        ↑
   Connect Orange
```

---

## ⚙️ How Continuous Rotation Control Works

### PWM Signal Explanation:

| Duty Cycle | Behavior |
|------------|----------|
| 5.0% | Full speed reverse (counterclockwise) |
| 7.5% | **STOP** (neutral position) |
| 10.0% | Full speed forward (clockwise) |

### Our Implementation:

```python
# Speed Level → Duty Cycle → Rotation Speed
Level 0: 7.5%  → Stopped
Level 1: 8.4%  → 20% forward speed
Level 2: 9.3%  → 40% forward speed
Level 3: 10.2% → 60% forward speed
Level 4: 11.1% → 80% forward speed
Level 5: 12.0% → 100% forward speed (maximum)
```

The motor continuously rotates when ON, getting faster as you increase the level.

---

## 🧪 Testing Your Servo

### Quick Test Script:

```python
#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time

SERVO_PIN = 13

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)
pwm = GPIO.PWM(SERVO_PIN, 50)  # 50Hz

try:
    # Test 1: Stop (neutral)
    print("Test 1: Stopped (7.5%)")
    pwm.start(7.5)
    time.sleep(3)
    
    # Test 2: Slow forward
    print("Test 2: Slow forward (8.5%)")
    pwm.ChangeDutyCycle(8.5)
    time.sleep(3)
    
    # Test 3: Medium forward
    print("Test 3: Medium forward (10%)")
    pwm.ChangeDutyCycle(10)
    time.sleep(3)
    
    # Test 4: Fast forward
    print("Test 4: Fast forward (11.5%)")
    pwm.ChangeDutyCycle(11.5)
    time.sleep(3)
    
    # Stop
    print("Stopping...")
    pwm.ChangeDutyCycle(7.5)
    time.sleep(1)
    
except KeyboardInterrupt:
    pass
finally:
    pwm.stop()
    GPIO.cleanup()
    print("Test complete!")
```

Save as `test_servo.py` and run:
```bash
sudo python3 test_servo.py
```

### Expected Behavior:
1. Motor should be stopped initially
2. Should start rotating slowly
3. Speed should increase progressively
4. Should stop at the end

### Troubleshooting Test Results:

**Motor doesn't stop at 7.5%:**
- Adjust the neutral value (try 7.0-8.0)
- Servo may need calibration
- Check if it's truly a continuous rotation servo

**Motor doesn't rotate:**
- Check wiring connections
- Verify 5V power supply
- Try external power supply
- Check if servo is damaged

**Motor rotates opposite direction:**
- That's okay! Some servos are wired differently
- Swap the duty cycle range in code (5-7.5% instead of 7.5-10%)

---

## 🔋 Power Considerations

### Current Draw:
- Continuous rotation servos draw more current than positional servos
- Expected: 100-500mA depending on load
- Peak: Up to 1A when starting or under load

### Power Options:

#### Option 1: Raspberry Pi 5V (Simple)
```
Pi 5V → Servo Red Wire
```
**Pros**: Simple, no extra hardware
**Cons**: May brownout Pi if servo draws too much current
**Good for**: Light loads, testing, small servos

#### Option 2: External 5V Power Supply (Recommended)
```
External 5V Supply → Servo Red Wire
Common Ground → Both Pi GND and Supply GND
```
**Pros**: Stable, no risk to Pi
**Cons**: Needs extra power supply
**Good for**: Production, heavy loads, multiple servos

### Recommended External Power:
- 5V 2A USB power adapter
- 4x AA battery pack (6V works fine)
- Bench power supply set to 5-6V

---

## 📊 Comparison: Before vs After

### Standard Positional Servo (Original):
| Feature | Value |
|---------|-------|
| Range | 0-180° |
| Control | Position |
| Use Case | Set to angle, hold position |

### Continuous Rotation Servo (Updated):
| Feature | Value |
|---------|-------|
| Range | 360° continuous |
| Control | Speed & direction |
| Use Case | Continuous motion, variable speed |

---

## 💡 Project Applications

What you can do with continuous rotation servo:

1. **Rotating Display Stand**
   - Showcase objects by rotating them
   - Control speed with gestures

2. **Fan Control**
   - Attach fan blade to servo shaft
   - Variable speed fan

3. **Conveyor Belt**
   - Small conveyor system
   - Adjustable speed

4. **Mixer/Stirrer**
   - Automatic stirring mechanism
   - Speed control

5. **Wheel Drive**
   - Small robot wheels
   - Vehicle control

---

## 🛡️ Safety Tips

1. **Current Protection**
   - Use external power for continuous operation
   - Add 1000µF capacitor across servo power pins
   - Monitor Pi for brownouts

2. **Mechanical Safety**
   - Don't block servo shaft when rotating
   - Use appropriate torque for your application
   - Secure servo to prevent movement

3. **Heat Management**
   - Servos get warm during continuous operation
   - Ensure adequate ventilation
   - Don't run at max speed for extended periods

4. **Wiring**
   - Double-check polarity before powering
   - Use proper gauge wire (22-24 AWG)
   - Secure connections to prevent shorts

---

## 📝 Code Configuration

### Adjusting Neutral Point:
If your servo doesn't stop at 7.5%, edit `gesture_control_system.py`:

```python
def set_servo_speed(self, level):
    # ... existing code ...
    base_stop = 7.5  # ← ADJUST THIS (try 7.0-8.0)
    # ... rest of code ...
```

### Adjusting Speed Range:
To change max speed:

```python
def set_servo_speed(self, level):
    # ... existing code ...
    base_stop = 7.5
    max_forward = 12.0  # ← ADJUST THIS (try 10.0-12.0)
    # ... rest of code ...
```

### Reverse Direction:
To make servo rotate opposite direction:

```python
def set_servo_speed(self, level):
    # ... existing code ...
    base_stop = 7.5
    max_reverse = 3.0  # Use reverse direction
    
    # Calculate for reverse
    speed_range = base_stop - max_reverse
    duty_cycle = base_stop - (self.motor_level / 5.0) * speed_range
    # ... rest of code ...
```

---

## 🎓 Learning Resources

### Tutorials:
- [Adafruit Servo Guide](https://learn.adafruit.com/adafruits-raspberry-pi-lesson-8-using-a-servo-motor)
- [Continuous Rotation Servo Basics](https://www.pololu.com/docs/servos)

### Video Guides:
- Search "continuous rotation servo raspberry pi"
- Search "convert SG90 to continuous rotation"

### Community:
- Raspberry Pi Forums
- r/raspberry_pi subreddit
- Arduino Forums (servo section)

---

## ✅ Quick Checklist

Before running the gesture control system:

- [ ] Have continuous rotation servo (FS90R, converted SG90, etc.)
- [ ] Wired correctly (Orange→GPIO13, Red→5V, Brown→GND)
- [ ] Tested servo responds to PWM signals
- [ ] Calibrated neutral stop point if needed
- [ ] External power supply if needed
- [ ] Servo securely mounted
- [ ] All connections secure

---

## 🆘 Common Issues

### "Servo won't stop at neutral"
→ Adjust `base_stop` value in code (try 7.0-8.0)

### "Servo rotates but very slowly"
→ Increase `max_forward` value (try up to 12.0)

### "Servo jitters or buzzes"
→ Check power supply, add capacitor, secure wiring

### "Raspberry Pi reboots when servo runs"
→ Use external power supply for servo

### "Wrong rotation direction"
→ Swap duty cycle range in code (see "Reverse Direction" above)

---

**You're all set! Your continuous rotation servo will now work perfectly with the gesture control system.** 🎉
