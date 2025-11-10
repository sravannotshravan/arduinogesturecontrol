#!/usr/bin/env python3
"""
Gesture Control CLIENT - Runs on Laptop
Performs gesture detection and sends control commands to Raspberry Pi server via WiFi

This program:
1. Captures video from laptop webcam
2. Detects hand gestures using MediaPipe
3. Sends control commands to Raspberry Pi server over network
4. Displays real-time feedback
"""

import cv2
import mediapipe as mp
import math
import time
import socket
import json
import threading

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
        
        # For thumb
        if finger_tip_id == 4:
            return tip.x < landmarks[3].x if landmarks[0].x < landmarks[9].x else tip.x > landmarks[3].x
        
        # For other fingers
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
        
        thumb_tip = landmarks[4]
        thumb_ip = landmarks[3]
        index_tip = landmarks[8]
        middle_tip = landmarks[12]
        wrist = landmarks[0]
        palm_center = landmarks[9]
        
        thumb_extended = 4 in extended_fingers
        
        # Thumbs Up Detection
        if thumb_extended and count == 1:
            if thumb_tip.y < wrist.y and thumb_tip.y < thumb_ip.y - 0.05:
                other_fingers_closed = all([
                    landmarks[8].y > landmarks[6].y,
                    landmarks[12].y > landmarks[10].y,
                    landmarks[16].y > landmarks[14].y,
                    landmarks[20].y > landmarks[18].y
                ])
                if other_fingers_closed:
                    return "THUMBS_UP"
        
        # Thumbs Down Detection
        if thumb_extended and count == 1:
            if thumb_tip.y > palm_center.y + 0.05:
                other_fingers_closed = all([
                    landmarks[8].y > landmarks[6].y,
                    landmarks[12].y > landmarks[10].y,
                    landmarks[16].y > landmarks[14].y,
                    landmarks[20].y > landmarks[18].y
                ])
                if other_fingers_closed:
                    return "THUMBS_DOWN"
        
        # Number 1 Detection
        if 8 in extended_fingers and count == 1 and not thumb_extended:
            return "ONE"
        
        # Number 2 Detection
        if 8 in extended_fingers and 12 in extended_fingers and count == 2:
            distance = self.calculate_distance(index_tip, middle_tip)
            if distance > 0.05:
                return "TWO"
        
        # Open Hand Detection
        if count >= 4 and thumb_extended:
            return "OPEN"
        
        # Closed Hand/Fist Detection
        if count == 0:
            avg_distance = sum([
                self.calculate_distance(palm_center, landmarks[tip])
                for tip in [4, 8, 12, 16, 20]
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


class NetworkClient:
    """Handles network communication with Raspberry Pi server"""
    
    def __init__(self, server_ip, server_port=5000):
        self.server_ip = server_ip
        self.server_port = server_port
        self.socket = None
        self.connected = False
        self.last_status = {}
        self.connection_thread = None
        
    def connect(self):
        """Connect to Raspberry Pi server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)
            print(f"Connecting to {self.server_ip}:{self.server_port}...")
            self.socket.connect((self.server_ip, self.server_port))
            self.connected = True
            print("✓ Connected to Raspberry Pi server!")
            
            # Start status receiver thread
            self.connection_thread = threading.Thread(target=self._receive_status, daemon=True)
            self.connection_thread.start()
            
            return True
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            self.connected = False
            return False
    
    def _receive_status(self):
        """Receive status updates from server"""
        while self.connected:
            try:
                data = self.socket.recv(4096)
                if data:
                    status = json.loads(data.decode('utf-8'))
                    self.last_status = status
            except socket.timeout:
                continue
            except Exception as e:
                if self.connected:
                    print(f"Status receive error: {e}")
                break
    
    def send_command(self, command_type, data=None):
        """Send command to Raspberry Pi"""
        if not self.connected:
            return False
        
        try:
            command = {
                'type': command_type,
                'data': data or {},
                'timestamp': time.time()
            }
            message = json.dumps(command) + '\n'
            self.socket.sendall(message.encode('utf-8'))
            return True
        except Exception as e:
            print(f"Send error: {e}")
            self.connected = False
            return False
    
    def get_status(self):
        """Get last received status from server"""
        return self.last_status
    
    def disconnect(self):
        """Disconnect from server"""
        self.connected = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        print("Disconnected from server")


def main():
    """Main client control loop"""
    print("=" * 60)
    print("GESTURE CONTROL CLIENT - LAPTOP")
    print("=" * 60)
    print("\nThis program detects gestures and sends commands to")
    print("Raspberry Pi server over WiFi")
    print("\nControls:")
    print("  1 finger (☝)  : Switch to LED control mode")
    print("  2 fingers (✌)  : Switch to Motor control mode")
    print("  Open hand (✋) : Turn ON current device")
    print("  Closed hand (✊): Turn OFF current device")
    print("  Thumbs up (👍) for 2s : Increase brightness/speed")
    print("  Thumbs down (👎) for 2s: Decrease brightness/speed")
    print("\nPress 'q' to quit")
    print("=" * 60)
    
    # Get server IP from user
    print("\nEnter Raspberry Pi IP address:")
    print("(Example: 192.168.1.100)")
    server_ip = input("IP: ").strip()
    
    if not server_ip:
        print("Error: No IP address provided")
        return
    
    # Initialize components
    print("\nInitializing...")
    detector = HandGestureDetector()
    client = NetworkClient(server_ip)
    
    # Connect to server
    if not client.connect():
        print("\nCannot connect to server. Make sure:")
        print("1. Raspberry Pi server is running")
        print("2. Both devices are on same WiFi network")
        print("3. IP address is correct")
        print("4. Firewall allows connection on port 5000")
        return
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    if not cap.isOpened():
        print("Error: Could not open camera")
        return
    
    print("\n✓ Camera initialized")
    print("✓ Starting gesture detection...\n")
    
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
            
            # Get status from server
            status = client.get_status()
            current_mode = status.get('mode', mode)
            led_status = status.get('led', {})
            motor_status = status.get('motor', {})
            
            # Display connection status
            conn_status = "CONNECTED" if client.connected else "DISCONNECTED"
            conn_color = (0, 255, 0) if client.connected else (0, 0, 255)
            cv2.putText(processed_frame, f"Server: {conn_status}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, conn_color, 2)
            
            # Display current mode
            mode_color = (0, 255, 255) if current_mode == "LED" else (255, 128, 0)
            cv2.putText(processed_frame, f"MODE: {current_mode}", (10, processed_frame.shape[0] - 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, mode_color, 2)
            
            # Display device status
            if current_mode == "LED":
                led_on = led_status.get('on', False)
                led_level = led_status.get('level', 0)
                status_text = f"LED: {'ON' if led_on else 'OFF'} - Level: {led_level}/5"
            else:
                motor_on = motor_status.get('on', False)
                motor_level = motor_status.get('level', 0)
                status_text = f"MOTOR: {'ON' if motor_on else 'OFF'} - Speed: {motor_level}/5"
            
            cv2.putText(processed_frame, status_text, (10, processed_frame.shape[0] - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Handle gestures and send commands
            if gesture and client.connected:
                # Mode switching
                if gesture == "ONE":
                    if current_mode != "LED":
                        mode = "LED"
                        client.send_command('mode', {'mode': 'LED'})
                        print("\n📍 Switched to LED control mode")
                
                elif gesture == "TWO":
                    if current_mode != "MOTOR":
                        mode = "MOTOR"
                        client.send_command('mode', {'mode': 'MOTOR'})
                        print("\n📍 Switched to MOTOR control mode")
                
                # On/Off controls
                elif gesture == "OPEN":
                    client.send_command('turn_on', {})
                    print(f"✋ Turn ON {current_mode}")
                
                elif gesture == "CLOSED":
                    client.send_command('turn_off', {})
                    print(f"✊ Turn OFF {current_mode}")
                
                # Thumbs up/down with 2-second hold
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
                                client.send_command('increase', {})
                                print(f"👍 Increase {current_mode}")
                            else:
                                client.send_command('decrease', {})
                                print(f"👎 Decrease {current_mode}")
                            
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
            
            # Display frame
            cv2.imshow('Gesture Control Client - Laptop', processed_frame)
            
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
        client.disconnect()
        print("\n✓ Client shutdown complete")


if __name__ == "__main__":
    main()
