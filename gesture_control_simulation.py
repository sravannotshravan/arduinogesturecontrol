#!/usr/bin/env python3
"""
Gesture Control System - SIMULATION MODE
Visualizes LED and Motor control without requiring Raspberry Pi hardware

This version runs on any computer and shows a graphical simulation of:
- LED with brightness levels (visual glow effect)
- Continuous rotation servo with speed visualization (rotating animation)
"""

import cv2
import mediapipe as mp
import math
import time
import numpy as np

class HandGestureDetector:
    def __init__(self):
        # Initialize MediaPipe Hand solution
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
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
        finger_tips = [4, 8, 12, 16, 20]
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


class DeviceSimulator:
    """Simulates LED and Servo Motor with visual representation"""
    
    def __init__(self):
        # State variables
        self.led_level = 0      # 0-5
        self.motor_level = 0    # 0-5
        self.led_on = False
        self.motor_on = False
        
        print("✓ Simulation Mode Initialized")
        print("  LED: Simulated (GPIO 18)")
        print("  Servo: Simulated (GPIO 13)")
    
    def draw_led(self, frame, x, y, size=80):
        """Draw LED with glow effect based on brightness level"""
        # LED bulb outline
        cv2.circle(frame, (x, y), size, (100, 100, 100), 2)
        
        if self.led_on and self.led_level > 0:
            # Calculate brightness
            intensity = int((self.led_level / 5.0) * 255)
            
            # Draw glowing LED with multiple circles for glow effect
            for i in range(5, 0, -1):
                alpha = (i / 5.0) * (self.led_level / 5.0)
                radius = size - (i * 8)
                color_val = int(intensity * alpha)
                cv2.circle(frame, (x, y), radius, 
                          (color_val // 2, color_val // 2, color_val), -1)
            
            # Core bright center
            cv2.circle(frame, (x, y), 20, (255, 255, 255), -1)
            
            # LED status text
            cv2.putText(frame, f"ON - {self.led_level}/5", 
                       (x - 50, y + size + 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        else:
            # OFF state - dark gray circle
            cv2.circle(frame, (x, y), size - 10, (50, 50, 50), -1)
            cv2.putText(frame, "OFF", (x - 25, y + size + 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        # Label
        cv2.putText(frame, "LED (GPIO 18)", (x - 60, y - size - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    def draw_servo(self, frame, x, y, size=100):
        """Draw servo motor with rotating indicator"""
        # Servo body (rectangle)
        cv2.rectangle(frame, (x - size, y - 40), (x + size, y + 40),
                     (150, 150, 150), -1)
        cv2.rectangle(frame, (x - size, y - 40), (x + size, y + 40),
                     (100, 100, 100), 3)
        
        # Servo shaft (circle)
        cv2.circle(frame, (x, y), 30, (80, 80, 80), -1)
        cv2.circle(frame, (x, y), 30, (50, 50, 50), 2)
        
        if self.motor_on and self.motor_level > 0:
            # Calculate rotation angle based on time and speed
            import time
            current_time = time.time()
            # Rotation speed increases with level
            rotation_speed = (self.motor_level / 5.0) * 360  # degrees per second
            angle = (current_time * rotation_speed) % 360
            angle_rad = math.radians(angle - 90)
            
            # Draw rotating arm
            arm_length = 70
            end_x = int(x + arm_length * math.cos(angle_rad))
            end_y = int(y + arm_length * math.sin(angle_rad))
            
            # Draw multiple arms for visual effect
            for i in range(3):
                offset_angle = angle_rad + (i * math.pi * 2 / 3)
                arm_x = int(x + 40 * math.cos(offset_angle))
                arm_y = int(y + 40 * math.sin(offset_angle))
                cv2.line(frame, (x, y), (arm_x, arm_y), (0, 200, 200), 3)
            
            # Main arm
            cv2.line(frame, (x, y), (end_x, end_y), (0, 255, 255), 5)
            cv2.circle(frame, (end_x, end_y), 10, (0, 200, 200), -1)
            
            # Draw rotation direction arrows
            arrow_radius = 55
            for arrow_offset in [0, 120, 240]:
                arrow_angle = math.radians(arrow_offset)
                arrow_x = int(x + arrow_radius * math.cos(arrow_angle))
                arrow_y = int(y + arrow_radius * math.sin(arrow_angle))
                # Draw small rotation indicator
                cv2.circle(frame, (arrow_x, arrow_y), 3, (255, 255, 0), -1)
            
            # Speed percentage
            speed_percent = (self.motor_level / 5.0) * 100
            
            # Status text
            cv2.putText(frame, f"ON - Speed {self.motor_level}/5 ({speed_percent:.0f}%)", 
                       (x - 100, y + 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # Rotation indicator
            cv2.putText(frame, "ROTATING >>", 
                       (x - 60, y - 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
        else:
            # OFF state - stationary arm
            cv2.line(frame, (x, y), (x - 70, y), (100, 100, 100), 5)
            cv2.circle(frame, (x - 70, y), 10, (80, 80, 80), -1)
            cv2.putText(frame, "OFF - STOPPED", (x - 70, y + 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        # Label
        cv2.putText(frame, "CONTINUOUS ROTATION SERVO (GPIO 13)", (x - 150, y - 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    def set_led_brightness(self, level):
        """Set LED brightness (0-5)"""
        self.led_level = max(0, min(5, level))
        if self.led_on and self.led_level > 0:
            duty_cycle = (self.led_level / 5.0) * 100
            print(f"💡 LED Brightness: {self.led_level}/5 ({duty_cycle:.1f}%)")
    
    def set_servo_speed(self, level):
        """Set servo motor rotation speed based on level (0-5)"""
        self.motor_level = max(0, min(5, level))
        if self.motor_on and self.motor_level > 0:
            speed_percent = (self.motor_level / 5.0) * 100
            print(f"⚙️  Servo Speed: {self.motor_level}/5 ({speed_percent:.0f}%)")
    
    def led_turn_on(self):
        """Turn LED on"""
        self.led_on = True
        if self.led_level == 0:
            self.led_level = 3
        self.set_led_brightness(self.led_level)
        print("💡 LED: ON")
    
    def led_turn_off(self):
        """Turn LED off"""
        self.led_on = False
        print("💡 LED: OFF")
    
    def motor_turn_on(self):
        """Turn motor on"""
        self.motor_on = True
        if self.motor_level == 0:
            self.motor_level = 3
        self.set_servo_speed(self.motor_level)
        print("⚙️  Motor: ON (Rotating)")
    
    def motor_turn_off(self):
        """Turn motor off"""
        self.motor_on = False
        print("⚙️  Motor: OFF (Stopped)")
    
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
        """Cleanup (no-op for simulation)"""
        print("✓ Simulation ended")


def main():
    """Main control loop with visualization"""
    print("=" * 60)
    print("GESTURE CONTROL SYSTEM - SIMULATION MODE")
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
    simulator = DeviceSimulator()
    detector = HandGestureDetector()
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    if not cap.isOpened():
        print("Error: Could not open camera")
        return
    
    # Create visualization window
    viz_width = 500
    viz_height = 480
    
    # Control state
    mode = "LED"
    last_gesture = None
    gesture_start_time = None
    HOLD_DURATION = 2.0
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame = cv2.flip(frame, 1)
            
            # Process frame and detect gesture
            processed_frame, gesture = detector.process_frame(frame)
            
            # Create visualization panel
            viz_panel = np.zeros((viz_height, viz_width, 3), dtype=np.uint8)
            viz_panel[:] = (40, 40, 40)  # Dark background
            
            # Draw devices on visualization panel
            simulator.draw_led(viz_panel, viz_width // 4, viz_height // 2, 60)
            simulator.draw_servo(viz_panel, 3 * viz_width // 4, viz_height // 2, 80)
            
            # Display current mode
            mode_color = (0, 255, 255) if mode == "LED" else (255, 128, 0)
            cv2.putText(processed_frame, f"MODE: {mode}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, mode_color, 2)
            
            # Display device status on camera frame
            if mode == "LED":
                status = f"LED: {'ON' if simulator.led_on else 'OFF'} - Level: {simulator.led_level}/5"
            else:
                status = f"MOTOR: {'ON' if simulator.motor_on else 'OFF'} - Level: {simulator.motor_level}/5"
            
            cv2.putText(processed_frame, status, 
                       (10, processed_frame.shape[0] - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Highlight active device on viz panel
            if mode == "LED":
                cv2.rectangle(viz_panel, (10, 10), (viz_width // 2 - 10, viz_height - 10),
                            (0, 255, 255), 3)
            else:
                cv2.rectangle(viz_panel, (viz_width // 2 + 10, 10), 
                            (viz_width - 10, viz_height - 10),
                            (255, 128, 0), 3)
            
            # Handle gestures
            if gesture:
                if gesture == "ONE":
                    if mode != "LED":
                        mode = "LED"
                        print("\n📍 Switched to LED control mode")
                
                elif gesture == "TWO":
                    if mode != "MOTOR":
                        mode = "MOTOR"
                        print("\n📍 Switched to MOTOR control mode")
                
                elif gesture == "OPEN":
                    if mode == "LED" and not simulator.led_on:
                        simulator.led_turn_on()
                    elif mode == "MOTOR" and not simulator.motor_on:
                        simulator.motor_turn_on()
                
                elif gesture == "CLOSED":
                    if mode == "LED" and simulator.led_on:
                        simulator.led_turn_off()
                    elif mode == "MOTOR" and simulator.motor_on:
                        simulator.motor_turn_off()
                
                elif gesture in ["THUMBS_UP", "THUMBS_DOWN"]:
                    if gesture != last_gesture:
                        last_gesture = gesture
                        gesture_start_time = time.time()
                        cv2.putText(processed_frame, "Hold for 2 seconds...", 
                                   (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 
                                   0.7, (0, 255, 255), 2)
                    else:
                        elapsed = time.time() - gesture_start_time
                        remaining = HOLD_DURATION - elapsed
                        
                        if elapsed >= HOLD_DURATION:
                            if gesture == "THUMBS_UP":
                                if mode == "LED":
                                    simulator.increase_led()
                                else:
                                    simulator.increase_motor()
                            else:
                                if mode == "LED":
                                    simulator.decrease_led()
                                else:
                                    simulator.decrease_motor()
                            
                            gesture_start_time = time.time()
                        else:
                            cv2.putText(processed_frame, 
                                       f"Hold: {remaining:.1f}s", 
                                       (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 
                                       0.7, (0, 255, 255), 2)
                else:
                    last_gesture = None
                    gesture_start_time = None
            else:
                last_gesture = None
                gesture_start_time = None
            
            # Combine frames side by side
            combined = np.hstack([processed_frame, viz_panel])
            
            # Display combined frame
            cv2.imshow('Gesture Control System - SIMULATION', combined)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        detector.close()
        simulator.cleanup()
        print("\n✓ Simulation shutdown complete")


if __name__ == "__main__":
    main()
