#!/usr/bin/env python3

import cv2
import mediapipe as mp
import math
import time
try:
    import RPi.GPIO as GPIO
except ImportError:
    print("Warning: RPi.GPIO not available. Running in simulation mode.")
    GPIO = None

class HandGestureDetector:
    def __init__(self):
        # Initialize MediaPipe Hand solution
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,  # Only detect one hand
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        
    def calculate_distance(self, point1, point2):
        """Calculate Euclidean distance between two points"""
        return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)
    
    def is_finger_extended(self, landmarks, finger_tip_id, finger_pip_id):
        """Check if a finger is extended"""
        tip = landmarks[finger_tip_id]
        pip = landmarks[finger_pip_id]
        
        # For thumb (different logic)
        if finger_tip_id == 4:
            return tip.x < landmarks[3].x if landmarks[0].x < landmarks[9].x else tip.x > landmarks[3].x
        
        # For other fingers, check if tip is above PIP
        return tip.y < pip.y
    
    def count_extended_fingers(self, landmarks):
        """Count how many fingers are extended"""
        finger_tips = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky
        finger_pips = [3, 6, 10, 14, 18]
        
        extended = []
        for tip_id, pip_id in zip(finger_tips, finger_pips):
            if self.is_finger_extended(landmarks, tip_id, pip_id):
                extended.append(tip_id)
        
        return len(extended), extended
    
    def detect_gesture(self, landmarks):
        """Detect specific hand gestures"""
        count, extended_fingers = self.count_extended_fingers(landmarks)
        
        # Get key landmarks
        thumb_tip = landmarks[4]
        thumb_ip = landmarks[3]
        index_tip = landmarks[8]
        middle_tip = landmarks[12]
        wrist = landmarks[0]
        palm_center = landmarks[9]
        
        # Check if thumb is truly extended (not just curled)
        thumb_extended = 4 in extended_fingers
        
        # Thumbs Up Detection - thumb extended and pointing up, other fingers closed
        if thumb_extended and count == 1:
            # Thumb tip should be significantly above wrist and thumb IP joint
            if thumb_tip.y < wrist.y and thumb_tip.y < thumb_ip.y - 0.05:
                # Verify other fingers are closed
                other_fingers_closed = all([
                    landmarks[8].y > landmarks[6].y,  # Index closed
                    landmarks[12].y > landmarks[10].y,  # Middle closed
                    landmarks[16].y > landmarks[14].y,  # Ring closed
                    landmarks[20].y > landmarks[18].y   # Pinky closed
                ])
                if other_fingers_closed:
                    return "THUMBS_UP"
        
        # Thumbs Down Detection - thumb extended and pointing down, other fingers closed
        if thumb_extended and count == 1:
            # Thumb tip should be significantly below palm center
            if thumb_tip.y > palm_center.y + 0.05:
                # Verify other fingers are closed
                other_fingers_closed = all([
                    landmarks[8].y > landmarks[6].y,  # Index closed
                    landmarks[12].y > landmarks[10].y,  # Middle closed
                    landmarks[16].y > landmarks[14].y,  # Ring closed
                    landmarks[20].y > landmarks[18].y   # Pinky closed
                ])
                if other_fingers_closed:
                    return "THUMBS_DOWN"
        
        # Number 1 Detection (only index finger up, thumb closed)
        if 8 in extended_fingers and count == 1 and not thumb_extended:
            return "ONE"
        
        # Number 2 Detection (index and middle finger up)
        if 8 in extended_fingers and 12 in extended_fingers and count == 2:
            distance = self.calculate_distance(index_tip, middle_tip)
            if distance > 0.05:
                return "TWO"
        
        # Open Hand Detection (all fingers extended including thumb)
        if count >= 4 and thumb_extended:
            return "OPEN"
        
        # Closed Hand/Fist Detection - all fingers closed INCLUDING thumb
        if count == 0:
            # Check that all fingertips are close to palm
            avg_distance = sum([
                self.calculate_distance(palm_center, landmarks[tip])
                for tip in [4, 8, 12, 16, 20]  # Include thumb
            ]) / 5
            
            if avg_distance < 0.12:
                return "CLOSED"
        
        return "UNKNOWN"
    
    def process_frame(self, frame):
        """Process a single frame and detect gestures"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        gesture = None
        
        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            
            # Draw hand landmarks
            self.mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                self.mp_hands.HAND_CONNECTIONS
            )
            
            # Detect gesture
            gesture = self.detect_gesture(hand_landmarks.landmark)
            
            # Display gesture name
            h, w, _ = frame.shape
            cv2.putText(frame, gesture, (10, 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
        
        return frame, gesture
    
    def close(self):
        """Release resources"""
        self.hands.close()


class DeviceController:
    """Controls LED and Servo Motor via GPIO"""
    
    # GPIO Pin assignments
    LED_PIN = 18      # GPIO 18 (Physical Pin 12) - PWM capable
    SERVO_PIN = 13    # GPIO 13 (Physical Pin 33) - PWM capable
    
    def __init__(self):
        if GPIO is None:
            raise RuntimeError("RPi.GPIO not available. Cannot control hardware.")
        
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Setup LED with PWM (1000 Hz)
        GPIO.setup(self.LED_PIN, GPIO.OUT)
        self.led_pwm = GPIO.PWM(self.LED_PIN, 1000)
        self.led_pwm.start(0)
        
        # Setup Servo with PWM (50 Hz for continuous rotation servo)
        GPIO.setup(self.SERVO_PIN, GPIO.OUT)
        self.servo_pwm = GPIO.PWM(self.SERVO_PIN, 50)
        self.servo_pwm.start(7.5)  # Start at neutral (stopped)
        
        # State variables
        self.led_level = 0      # 0-5 (0=off, 1-5=brightness levels)
        self.motor_level = 0    # 0-5 (0=off, 1-5=rotation speed levels)
        self.led_on = False
        self.motor_on = False
        
        print(f"✓ GPIO Initialized")
        print(f"  LED Pin: GPIO {self.LED_PIN} (Physical Pin 12)")
        print(f"  Servo Pin: GPIO {self.SERVO_PIN} (Physical Pin 33)")
        print(f"  Note: Using continuous rotation servo mode")
    
    def set_led_brightness(self, level):
        """Set LED brightness (0-5)"""
        self.led_level = max(0, min(5, level))
        if self.led_on and self.led_level > 0:
            duty_cycle = (self.led_level / 5.0) * 100
            self.led_pwm.ChangeDutyCycle(duty_cycle)
            print(f"💡 LED Brightness: {self.led_level}/5 ({duty_cycle:.1f}%)")
        else:
            self.led_pwm.ChangeDutyCycle(0)
    
    def set_servo_speed(self, level):
        """Set servo motor rotation speed based on level (0-5)"""
        self.motor_level = max(0, min(5, level))
        if self.motor_on and self.motor_level > 0:
            # Map level 1-5 to rotation speed
            # For continuous rotation servo:
            # 0% duty cycle = full speed reverse
            # 7.5% duty cycle = stop
            # 10-12% duty cycle = full speed forward
            # We'll use 7.5-12% for forward rotation at different speeds
            base_stop = 7.5  # Neutral position (no rotation)
            max_forward = 12.0  # Maximum forward speed
            
            # Calculate duty cycle for the speed level (1-5)
            speed_range = max_forward - base_stop
            duty_cycle = base_stop + (self.motor_level / 5.0) * speed_range
            
            self.servo_pwm.ChangeDutyCycle(duty_cycle)
            speed_percent = (self.motor_level / 5.0) * 100
            print(f"⚙️  Servo Speed: {self.motor_level}/5 ({speed_percent:.0f}% forward)")
        else:
            # Stop the motor (neutral position)
            self.servo_pwm.ChangeDutyCycle(7.5)
            time.sleep(0.1)
            self.servo_pwm.ChangeDutyCycle(0)
    
    def led_turn_on(self):
        """Turn LED on"""
        self.led_on = True
        if self.led_level == 0:
            self.led_level = 3  # Default to middle brightness
        self.set_led_brightness(self.led_level)
        print("💡 LED: ON")
    
    def led_turn_off(self):
        """Turn LED off"""
        self.led_on = False
        self.led_pwm.ChangeDutyCycle(0)
        print("💡 LED: OFF")
    
    def motor_turn_on(self):
        """Turn motor on"""
        self.motor_on = True
        if self.motor_level == 0:
            self.motor_level = 3  # Default to middle speed
        self.set_servo_speed(self.motor_level)
        print("⚙️  Motor: ON")
    
    def motor_turn_off(self):
        """Turn motor off"""
        self.motor_on = False
        self.servo_pwm.ChangeDutyCycle(7.5)  # Stop rotation (neutral)
        time.sleep(0.1)
        self.servo_pwm.ChangeDutyCycle(0)
        print("⚙️  Motor: OFF")
    
    def increase_led(self):
        """Increase LED brightness by 1 step"""
        if self.led_on:
            self.set_led_brightness(self.led_level + 1)
    
    def decrease_led(self):
        """Decrease LED brightness by 1 step"""
        if self.led_on:
            self.set_led_brightness(self.led_level - 1)
    
    def increase_motor(self):
        """Increase motor rotation speed by 1 step"""
        if self.motor_on:
            self.set_servo_speed(self.motor_level + 1)
    
    def decrease_motor(self):
        """Decrease motor rotation speed by 1 step"""
        if self.motor_on:
            self.set_servo_speed(self.motor_level - 1)
    
    def cleanup(self):
        """Cleanup GPIO"""
        self.led_pwm.stop()
        self.servo_pwm.stop()
        GPIO.cleanup()
        print("✓ GPIO Cleaned up")


def main():
    """Main control loop"""
    print("=" * 60)
    print("GESTURE-CONTROLLED LED & SERVO MOTOR SYSTEM")
    print("=" * 60)
    print("\nControls:")
    print("  1 finger (☝)  : Switch to LED control mode")
    print("  2 fingers (✌)  : Switch to Motor control mode")
    print("  Open hand (✋) : Turn ON current device")
    print("  Closed hand (✊): Turn OFF current device")
    print("  Thumbs up (👍) for 2s : Increase brightness/speed")
    print("  Thumbs down (👎) for 2s: Decrease brightness/speed")
    print("\nPress 'q' to quit\n")
    print("=" * 60)
    
    # Initialize components
    try:
        controller = DeviceController()
    except RuntimeError as e:
        print(f"Error: {e}")
        return
    
    detector = HandGestureDetector()
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    if not cap.isOpened():
        print("Error: Could not open camera")
        return
    
    # Control state
    mode = "LED"  # Current mode: "LED" or "MOTOR"
    
    # Gesture timing for thumbs up/down (need 2 seconds)
    last_gesture = None
    gesture_start_time = None
    HOLD_DURATION = 2.0  # seconds
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame = cv2.flip(frame, 1)
            
            # Process frame and detect gesture
            processed_frame, gesture = detector.process_frame(frame)
            
            # Display current mode and status
            mode_color = (0, 255, 255) if mode == "LED" else (255, 128, 0)
            cv2.putText(processed_frame, f"MODE: {mode}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, mode_color, 2)
            
            # Display device status
            if mode == "LED":
                status = f"LED: {'ON' if controller.led_on else 'OFF'} - Level: {controller.led_level}/5"
            else:
                status = f"MOTOR: {'ON' if controller.motor_on else 'OFF'} - Level: {controller.motor_level}/5"
            
            cv2.putText(processed_frame, status, (10, processed_frame.shape[0] - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Handle gestures
            if gesture:
                # Mode switching
                if gesture == "ONE":
                    if mode != "LED":
                        mode = "LED"
                        print("\n📍 Switched to LED control mode")
                
                elif gesture == "TWO":
                    if mode != "MOTOR":
                        mode = "MOTOR"
                        print("\n📍 Switched to MOTOR control mode")
                
                # On/Off controls
                elif gesture == "OPEN":
                    if mode == "LED" and not controller.led_on:
                        controller.led_turn_on()
                    elif mode == "MOTOR" and not controller.motor_on:
                        controller.motor_turn_on()
                
                elif gesture == "CLOSED":
                    if mode == "LED" and controller.led_on:
                        controller.led_turn_off()
                    elif mode == "MOTOR" and controller.motor_on:
                        controller.motor_turn_off()
                
                # Thumbs up/down with 2-second hold
                elif gesture in ["THUMBS_UP", "THUMBS_DOWN"]:
                    if gesture != last_gesture:
                        # New gesture detected
                        last_gesture = gesture
                        gesture_start_time = time.time()
                        cv2.putText(processed_frame, "Hold for 2 seconds...", 
                                   (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 
                                   0.7, (0, 255, 255), 2)
                    else:
                        # Same gesture, check duration
                        elapsed = time.time() - gesture_start_time
                        remaining = HOLD_DURATION - elapsed
                        
                        if elapsed >= HOLD_DURATION:
                            # Execute action
                            if gesture == "THUMBS_UP":
                                if mode == "LED":
                                    controller.increase_led()
                                else:
                                    controller.increase_motor()
                            else:  # THUMBS_DOWN
                                if mode == "LED":
                                    controller.decrease_led()
                                else:
                                    controller.decrease_motor()
                            
                            # Reset timer
                            gesture_start_time = time.time()
                        else:
                            # Show countdown
                            cv2.putText(processed_frame, 
                                       f"Hold: {remaining:.1f}s", 
                                       (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 
                                       0.7, (0, 255, 255), 2)
                else:
                    # Reset gesture timing for other gestures
                    last_gesture = None
                    gesture_start_time = None
            else:
                # No gesture detected, reset timing
                last_gesture = None
                gesture_start_time = None
            
            # Display frame
            cv2.imshow('Gesture Control System - Raspberry Pi 5', processed_frame)
            
            # Check for quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    
    finally:
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        detector.close()
        controller.cleanup()
        print("\n✓ System shutdown complete")


if __name__ == "__main__":
    main()
