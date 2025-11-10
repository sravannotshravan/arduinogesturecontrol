#!/usr/bin/env python3
"""
Gesture Control Client - Arduino USB Serial Version
Runs on laptop with webcam and connects to Arduino via USB Serial

This program:
1. Detects hand gestures using laptop's webcam
2. Sends control commands to Arduino via USB serial
3. Receives status updates from Arduino
4. Displays visual feedback on screen
"""

import cv2
import mediapipe as mp
import math
import time
import serial
import serial.tools.list_ports
import threading
import tkinter as tk
from tkinter import scrolledtext, ttk
from datetime import datetime

class HandGestureDetector:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        
    def calculate_distance(self, point1, point2):
        return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)
    
    def is_finger_extended(self, landmarks, finger_tip_id, finger_pip_id):
        tip = landmarks[finger_tip_id]
        pip = landmarks[finger_pip_id]
        
        if finger_tip_id == 4:
            return tip.x < landmarks[3].x if landmarks[0].x < landmarks[9].x else tip.x > landmarks[3].x
        
        return tip.y < pip.y
    
    def count_extended_fingers(self, landmarks):
        finger_tips = [4, 8, 12, 16, 20]
        finger_pips = [3, 6, 10, 14, 18]
        
        extended = []
        for tip_id, pip_id in zip(finger_tips, finger_pips):
            if self.is_finger_extended(landmarks, tip_id, pip_id):
                extended.append(tip_id)
        
        return len(extended), extended
    
    def detect_gesture(self, landmarks):
        count, extended_fingers = self.count_extended_fingers(landmarks)
        
        thumb_tip = landmarks[4]
        thumb_ip = landmarks[3]
        index_tip = landmarks[8]
        middle_tip = landmarks[12]
        ring_tip = landmarks[16]
        wrist = landmarks[0]
        palm_center = landmarks[9]
        
        thumb_extended = 4 in extended_fingers
        
        # Number 1 - Only index finger
        if 8 in extended_fingers and count == 1 and not thumb_extended:
            return "ONE"
        
        # Number 2 - Index and middle fingers
        if 8 in extended_fingers and 12 in extended_fingers and count == 2 and not thumb_extended:
            distance = self.calculate_distance(index_tip, middle_tip)
            if distance > 0.05:
                return "TWO"
        
        # Number 3 - Index, middle, and ring fingers
        if (8 in extended_fingers and 12 in extended_fingers and 
            16 in extended_fingers and count == 3 and not thumb_extended):
            return "THREE"
        
        # Number 4 - All four fingers (no thumb)
        if (8 in extended_fingers and 12 in extended_fingers and 
            16 in extended_fingers and 20 in extended_fingers and 
            count == 4 and not thumb_extended):
            return "FOUR"
        
        # Open Hand - All fingers including thumb
        if count >= 4 and thumb_extended:
            return "OPEN"
        
        # Closed Fist
        if count == 0:
            avg_distance = sum([
                self.calculate_distance(palm_center, landmarks[tip])
                for tip in [4, 8, 12, 16, 20]
            ]) / 5
            
            if avg_distance < 0.12:
                return "CLOSED"
        
        return "UNKNOWN"
    
    def process_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        gesture = None
        
        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            
            self.mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                self.mp_hands.HAND_CONNECTIONS
            )
            
            gesture = self.detect_gesture(hand_landmarks.landmark)
            
            h, w, _ = frame.shape
            cv2.putText(frame, gesture, (10, 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
        
        return frame, gesture
    
    def close(self):
        self.hands.close()


class ArduinoController:
    def __init__(self, port=None, baudrate=115200, log_callback=None):
        self.serial_conn = None
        self.port = port
        self.baudrate = baudrate
        self.mode = "LED"
        self.led_on = False
        self.led_level = 3
        self.motor_on = False
        self.motor_level = 3
        self.connected = False
        self.status_thread = None
        self.running = False
        self.log_callback = log_callback  # Callback for logging
        
    def find_arduino(self):
        """Auto-detect Arduino port"""
        ports = serial.tools.list_ports.comports()
        
        print("\nAvailable serial ports:")
        for i, port in enumerate(ports):
            print(f"  {i+1}. {port.device} - {port.description}")
        
        # Look for Arduino
        for port in ports:
            if 'Arduino' in port.description or 'CH340' in port.description or 'USB Serial' in port.description:
                print(f"\n✓ Found Arduino at: {port.device}")
                return port.device
        
        return None
    
    def connect(self):
        """Connect to Arduino"""
        try:
            if self.port is None:
                self.port = self.find_arduino()
                
                if self.port is None:
                    print("\n✗ No Arduino found automatically")
                    self.port = input("Enter COM port manually (e.g., COM3): ").strip()
            
            print(f"\nConnecting to Arduino on {self.port}...")
            self.serial_conn = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(2)  # Wait for Arduino to reset
            
            # Wait for ready message
            start_time = time.time()
            while time.time() - start_time < 5:
                if self.serial_conn.in_waiting:
                    line = self.serial_conn.readline().decode('utf-8').strip()
                    print(f"Arduino: {line}")
                    if line.startswith("READY:"):
                        self.connected = True
                        print("✓ Connected to Arduino successfully!")
                        
                        # Start status monitoring thread
                        self.running = True
                        self.status_thread = threading.Thread(target=self._monitor_responses, daemon=True)
                        self.status_thread.start()
                        
                        return True
            
            print("✗ Arduino did not respond")
            return False
            
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            return False
    
    def _monitor_responses(self):
        """Monitor responses from Arduino"""
        buffer = ""
        while self.running and self.serial_conn and self.serial_conn.is_open:
            try:
                if self.serial_conn.in_waiting:
                    data = self.serial_conn.read(self.serial_conn.in_waiting).decode('utf-8')
                    buffer += data
                    
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        line = line.strip()
                        if line:
                            self._log(f"← Arduino: {line}")
                            self._process_response(line)
                
                time.sleep(0.01)
            except:
                break
    
    def _log(self, message):
        """Log message using callback"""
        if self.log_callback:
            self.log_callback(message)
    
    def _process_response(self, line):
        """Process response from Arduino"""
        if line.startswith("STATUS:"):
            # Parse: STATUS:mode,led_state,led_level,motor_state,motor_level
            parts = line[7:].split(',')
            if len(parts) == 5:
                self.mode = parts[0]
                self.led_on = parts[1] == "ON"
                self.led_level = int(parts[2])
                self.motor_on = parts[3] == "ON"
                self.motor_level = int(parts[4])
        elif line.startswith("MODE:"):
            self.mode = line[5:]
        elif line.startswith("LED:"):
            if "ON" in line:
                self.led_on = True
            elif "OFF" in line:
                self.led_on = False
            elif "LEVEL:" in line:
                parts = line.split(':')
                if len(parts) >= 3:
                    self.led_level = int(parts[2])
        elif line.startswith("MOTOR:"):
            if "ON" in line:
                self.motor_on = True
            elif "OFF" in line:
                self.motor_on = False
            elif "LEVEL:" in line:
                parts = line.split(':')
                if len(parts) >= 3:
                    self.motor_level = int(parts[2])
    
    def send_command(self, command):
        """Send command to Arduino"""
        if self.connected and self.serial_conn:
            try:
                self._log(f"→ Laptop: {command}")
                self.serial_conn.write(f"{command}\n".encode('utf-8'))
                self.serial_conn.flush()
                return True
            except:
                return False
        return False
    
    def set_mode(self, mode):
        """Switch control mode"""
        self.send_command(f"MODE:{mode}")
    
    def turn_on(self):
        """Turn on current device"""
        if self.mode == "LED":
            self.send_command("LED:ON")
        else:
            self.send_command("MOTOR:ON")
    
    def turn_off(self):
        """Turn off current device"""
        if self.mode == "LED":
            self.send_command("LED:OFF")
        else:
            self.send_command("MOTOR:OFF")
    
    def increase(self):
        """Increase brightness/speed"""
        if self.mode == "LED":
            self.send_command("LED:UP")
        else:
            self.send_command("MOTOR:UP")
    
    def decrease(self):
        """Decrease brightness/speed"""
        if self.mode == "LED":
            self.send_command("LED:DOWN")
        else:
            self.send_command("MOTOR:DOWN")
    
    def disconnect(self):
        """Disconnect from Arduino"""
        self.running = False
        if self.serial_conn:
            self.serial_conn.close()
        print("\n✓ Disconnected from Arduino")


class ControlPanelGUI:
    def __init__(self, arduino_controller):
        self.arduino = arduino_controller
        self.root = tk.Tk()
        self.root.title("Arduino Control Panel")
        self.root.geometry("700x600")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Create main frames
        self.create_widgets()
        
        # Start update loop
        self.update_status()
        
    def create_widgets(self):
        # Title
        title = tk.Label(self.root, text="🎮 Gesture Control Panel", 
                        font=("Arial", 16, "bold"), bg="#2c3e50", fg="white", pady=10)
        title.pack(fill=tk.X)
        
        # Control Frame
        control_frame = tk.LabelFrame(self.root, text="Manual Controls", 
                                     font=("Arial", 12, "bold"), padx=10, pady=10)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Mode Selection
        mode_frame = tk.Frame(control_frame)
        mode_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(mode_frame, text="Mode:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        
        self.led_mode_btn = tk.Button(mode_frame, text="💡 LED", width=10, 
                                      command=lambda: self.set_mode("LED"),
                                      bg="#f39c12", fg="white", font=("Arial", 10, "bold"))
        self.led_mode_btn.pack(side=tk.LEFT, padx=5)
        
        self.motor_mode_btn = tk.Button(mode_frame, text="⚙️ MOTOR", width=10,
                                       command=lambda: self.set_mode("MOTOR"),
                                       bg="#95a5a6", fg="white", font=("Arial", 10, "bold"))
        self.motor_mode_btn.pack(side=tk.LEFT, padx=5)
        
        # LED Controls
        led_frame = tk.LabelFrame(control_frame, text="LED Controls", 
                                 font=("Arial", 10, "bold"))
        led_frame.pack(fill=tk.X, pady=5)
        
        led_buttons = tk.Frame(led_frame)
        led_buttons.pack(pady=5)
        
        tk.Button(led_buttons, text="ON", width=7, bg="#27ae60", fg="white",
                 command=lambda: self.arduino.send_command("LED:ON")).pack(side=tk.LEFT, padx=2)
        tk.Button(led_buttons, text="OFF", width=7, bg="#c0392b", fg="white",
                 command=lambda: self.arduino.send_command("LED:OFF")).pack(side=tk.LEFT, padx=2)
        tk.Button(led_buttons, text="↑ UP", width=7, bg="#3498db", fg="white",
                 command=lambda: self.arduino.send_command("LED:UP")).pack(side=tk.LEFT, padx=2)
        tk.Button(led_buttons, text="↓ DOWN", width=7, bg="#9b59b6", fg="white",
                 command=lambda: self.arduino.send_command("LED:DOWN")).pack(side=tk.LEFT, padx=2)
        
        # LED Level Display
        self.led_level_var = tk.StringVar(value="LED: OFF (Level 3/5)")
        tk.Label(led_frame, textvariable=self.led_level_var, 
                font=("Arial", 10)).pack(pady=5)
        
        # Motor Controls
        motor_frame = tk.LabelFrame(control_frame, text="Motor Controls", 
                                   font=("Arial", 10, "bold"))
        motor_frame.pack(fill=tk.X, pady=5)
        
        motor_buttons = tk.Frame(motor_frame)
        motor_buttons.pack(pady=5)
        
        tk.Button(motor_buttons, text="ON", width=7, bg="#27ae60", fg="white",
                 command=lambda: self.arduino.send_command("MOTOR:ON")).pack(side=tk.LEFT, padx=2)
        tk.Button(motor_buttons, text="OFF", width=7, bg="#c0392b", fg="white",
                 command=lambda: self.arduino.send_command("MOTOR:OFF")).pack(side=tk.LEFT, padx=2)
        tk.Button(motor_buttons, text="↑ UP", width=7, bg="#3498db", fg="white",
                 command=lambda: self.arduino.send_command("MOTOR:UP")).pack(side=tk.LEFT, padx=2)
        tk.Button(motor_buttons, text="↓ DOWN", width=7, bg="#9b59b6", fg="white",
                 command=lambda: self.arduino.send_command("MOTOR:DOWN")).pack(side=tk.LEFT, padx=2)
        
        # Emergency Stop Button
        emergency_frame = tk.Frame(control_frame, bg="#e74c3c", relief=tk.RAISED, bd=3)
        emergency_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(emergency_frame, text="⛔ EMERGENCY STOP ⛔", width=40, 
                 bg="#e74c3c", fg="white", font=("Arial", 12, "bold"),
                 command=self.emergency_stop,
                 activebackground="#c0392b").pack(pady=10)
        
        # Motor Level Display
        self.motor_level_var = tk.StringVar(value="MOTOR: OFF (Level 3/5)")
        tk.Label(motor_frame, textvariable=self.motor_level_var, 
                font=("Arial", 10)).pack(pady=5)
        
        # Status Frame
        status_frame = tk.LabelFrame(self.root, text="Current Status", 
                                    font=("Arial", 12, "bold"), padx=10, pady=10)
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.current_mode_var = tk.StringVar(value="Mode: LED")
        tk.Label(status_frame, textvariable=self.current_mode_var, 
                font=("Arial", 11, "bold"), fg="#2980b9").pack()
        
        # Serial Log Frame
        log_frame = tk.LabelFrame(self.root, text="Serial Communication Log", 
                                 font=("Arial", 12, "bold"), padx=10, pady=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Serial log text area
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, 
                                                  font=("Courier", 9),
                                                  bg="#1e1e1e", fg="#00ff00",
                                                  insertbackground="white")
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Clear log button
        tk.Button(log_frame, text="Clear Log", command=self.clear_log,
                 bg="#34495e", fg="white").pack(pady=5)
        
        # Initial log message
        self.add_log("=== Control Panel Started ===")
    
    def set_mode(self, mode):
        """Set control mode"""
        self.arduino.set_mode(mode)
        self.add_log(f"[USER] Mode switched to {mode}")
    
    def emergency_stop(self):
        """Emergency stop - turn off both LED and Motor and close program"""
        self.arduino.send_command("STOP")
        self.add_log("[EMERGENCY] ⛔ STOP BUTTON PRESSED - SHUTTING DOWN ⛔")
        self.root.after(500, self.shutdown_program)
    
    def shutdown_program(self):
        """Shutdown the entire program"""
        self.add_log("[SYSTEM] Shutting down program...")
        self.root.quit()
        self.root.destroy()
    
    def add_log(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
    
    def clear_log(self):
        """Clear log text"""
        self.log_text.delete(1.0, tk.END)
        self.add_log("=== Log Cleared ===")
    
    def update_status(self):
        """Update status display"""
        # Update mode display
        self.current_mode_var.set(f"Current Mode: {self.arduino.mode}")
        
        # Update LED status
        led_state = "ON" if self.arduino.led_on else "OFF"
        self.led_level_var.set(f"LED: {led_state} (Level {self.arduino.led_level}/5)")
        
        # Update Motor status
        motor_state = "ON" if self.arduino.motor_on else "OFF"
        self.motor_level_var.set(f"MOTOR: {motor_state} (Level {self.arduino.motor_level}/5)")
        
        # Update button colors based on mode
        if self.arduino.mode == "LED":
            self.led_mode_btn.config(bg="#f39c12", relief=tk.SUNKEN)
            self.motor_mode_btn.config(bg="#95a5a6", relief=tk.RAISED)
        else:
            self.led_mode_btn.config(bg="#95a5a6", relief=tk.RAISED)
            self.motor_mode_btn.config(bg="#e67e22", relief=tk.SUNKEN)
        
        # Schedule next update
        self.root.after(100, self.update_status)
    
    def on_closing(self):
        """Handle window close"""
        self.add_log("=== Control Panel Closing ===")
        self.root.quit()


def main():
    print("=" * 60)
    print("GESTURE CONTROL CLIENT - ARDUINO USB")
    print("=" * 60)
    print("\nHardware:")
    print("  LED: Arduino Pin 11 (PWM)")
    print("  Motor: Arduino Pin 8 (PWM)")
    print("\nGesture Controls:")
    print("  1 finger (☝)     : Switch to LED control mode")
    print("  2 fingers (✌)    : Switch to Motor control mode")
    print("  3 fingers (🤟)   : Increase brightness/speed (hold 2s)")
    print("  4 fingers (🖖)   : Decrease brightness/speed (hold 2s)")
    print("  Open hand (✋)    : Turn ON current device")
    print("  Closed hand (✊) : Turn OFF current device")
    print("\nControl Panel: Use GUI for manual control and serial logs")
    print("  ⛔ EMERGENCY STOP button turns off everything!")
    print("\nPress 'q' in camera window to quit\n")
    print("=" * 60)
    
    # Create control panel GUI first
    control_panel = None
    
    def log_callback(message):
        """Callback for logging to GUI"""
        if control_panel:
            control_panel.root.after(0, lambda: control_panel.add_log(message))
    
    # Initialize Arduino connection with logging
    arduino = ArduinoController(log_callback=log_callback)
    if not arduino.connect():
        print("\nFailed to connect to Arduino. Please check:")
        print("  1. Arduino is connected via USB")
        print("  2. Correct drivers are installed")
        print("  3. Arduino code is uploaded")
        return
    
    # Create control panel GUI
    control_panel = ControlPanelGUI(arduino)
    
    # Small delay to ensure GUI is ready
    time.sleep(0.5)
    
    # Initialize gesture detector
    detector = HandGestureDetector()
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    if not cap.isOpened():
        print("Error: Could not open camera")
        arduino.disconnect()
        return
    
    print("\n✓ Camera opened successfully")
    print("✓ System ready!\n")
    
    # Gesture timing
    last_gesture = None
    gesture_start_time = None
    HOLD_DURATION = 2.0
    
    def process_camera():
        """Process camera frames"""
        nonlocal last_gesture, gesture_start_time
        
        ret, frame = cap.read()
        if not ret:
            return False
        
        frame = cv2.flip(frame, 1)
        
        # Process gesture
        processed_frame, gesture = detector.process_frame(frame)
        
        # Display status
        mode_color = (0, 255, 255) if arduino.mode == "LED" else (255, 128, 0)
        cv2.putText(processed_frame, f"MODE: {arduino.mode}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, mode_color, 2)
        
        # Device status
        if arduino.mode == "LED":
            status = f"LED: {'ON' if arduino.led_on else 'OFF'} ({arduino.led_level}/5)"
        else:
            status = f"MOTOR: {'ON' if arduino.motor_on else 'OFF'} ({arduino.motor_level}/5)"
        
        cv2.putText(processed_frame, status, (10, processed_frame.shape[0] - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Handle gestures
        if gesture:
            # Mode switching
            if gesture == "ONE":
                if arduino.mode != "LED":
                    arduino.set_mode("LED")
                    print("\n📍 Switched to LED control mode")
                    if control_panel:
                        control_panel.root.after(0, lambda: control_panel.add_log("[GESTURE] Switched to LED mode (1 finger)"))
            
            elif gesture == "TWO":
                if arduino.mode != "MOTOR":
                    arduino.set_mode("MOTOR")
                    print("\n📍 Switched to MOTOR control mode")
                    if control_panel:
                        control_panel.root.after(0, lambda: control_panel.add_log("[GESTURE] Switched to MOTOR mode (2 fingers)"))
            
            # On/Off
            elif gesture == "OPEN":
                arduino.turn_on()
                if control_panel:
                    control_panel.root.after(0, lambda: control_panel.add_log(f"[GESTURE] Turn ON {arduino.mode} (open hand)"))
            
            elif gesture == "CLOSED":
                arduino.turn_off()
                if control_panel:
                    control_panel.root.after(0, lambda: control_panel.add_log(f"[GESTURE] Turn OFF {arduino.mode} (closed fist)"))
            
            # Three fingers - Increase (with hold)
            elif gesture == "THREE":
                if gesture != last_gesture:
                    last_gesture = gesture
                    gesture_start_time = time.time()
                    cv2.putText(processed_frame, "Hold 3 fingers for 2 seconds...", 
                               (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 
                               0.7, (0, 255, 255), 2)
                else:
                    elapsed = time.time() - gesture_start_time
                    remaining = HOLD_DURATION - elapsed
                    
                    if elapsed >= HOLD_DURATION:
                        arduino.increase()
                        if control_panel:
                            control_panel.root.after(0, lambda: control_panel.add_log(f"[GESTURE] Increase {arduino.mode} (3 fingers)"))
                        gesture_start_time = time.time()
                    else:
                        cv2.putText(processed_frame, 
                                   f"Hold: {remaining:.1f}s", 
                                   (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 
                                   0.7, (0, 255, 255), 2)
            
            # Four fingers - Decrease (with hold)
            elif gesture == "FOUR":
                if gesture != last_gesture:
                    last_gesture = gesture
                    gesture_start_time = time.time()
                    cv2.putText(processed_frame, "Hold 4 fingers for 2 seconds...", 
                               (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 
                               0.7, (0, 255, 255), 2)
                else:
                    elapsed = time.time() - gesture_start_time
                    remaining = HOLD_DURATION - elapsed
                    
                    if elapsed >= HOLD_DURATION:
                        arduino.decrease()
                        if control_panel:
                            control_panel.root.after(0, lambda: control_panel.add_log(f"[GESTURE] Decrease {arduino.mode} (4 fingers)"))
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
        
        # Display
        cv2.imshow('Gesture Control - Arduino USB', processed_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            return False
        
        return True
    
    def camera_loop():
        """Camera processing loop"""
        try:
            while process_camera():
                pass
        except KeyboardInterrupt:
            print("\n\nInterrupted by user")
        finally:
            cap.release()
            cv2.destroyAllWindows()
            detector.close()
            arduino.disconnect()
            print("\n✓ System shutdown complete")
            control_panel.root.quit()
    
    # Start camera in separate thread
    camera_thread = threading.Thread(target=camera_loop, daemon=True)
    camera_thread.start()
    
    # Run GUI in main thread
    try:
        control_panel.root.mainloop()
    except KeyboardInterrupt:
        pass
    finally:
        arduino.disconnect()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
