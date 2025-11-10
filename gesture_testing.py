#!/usr/bin/env python3
"""
Gesture Testing Program
Tests all gesture detection without controlling any hardware
Shows detection accuracy and provides real-time feedback
"""

import cv2
import mediapipe as mp
import math
import time

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
        
        # Gesture statistics
        self.gesture_counts = {
            "ONE": 0,
            "TWO": 0,
            "OPEN": 0,
            "CLOSED": 0,
            "THUMBS_UP": 0,
            "THUMBS_DOWN": 0,
            "UNKNOWN": 0
        }
        self.last_gesture = None
        self.gesture_duration = 0
        self.gesture_start_time = None
        
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
    
    def update_statistics(self, gesture):
        """Update gesture statistics"""
        if gesture in self.gesture_counts:
            if gesture != self.last_gesture:
                # New gesture detected
                if self.last_gesture:
                    self.gesture_counts[self.last_gesture] += 1
                self.last_gesture = gesture
                self.gesture_start_time = time.time()
            
            # Update duration
            if gesture == self.last_gesture and self.gesture_start_time:
                self.gesture_duration = time.time() - self.gesture_start_time
    
    def process_frame(self, frame):
        """Process a single frame and detect gestures"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        gesture = None
        finger_count = 0
        
        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            
            # Draw hand landmarks
            self.mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                self.mp_hands.HAND_CONNECTIONS,
                self.mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                self.mp_draw.DrawingSpec(color=(255, 255, 0), thickness=2)
            )
            
            # Detect gesture
            gesture = self.detect_gesture(hand_landmarks.landmark)
            finger_count, _ = self.count_extended_fingers(hand_landmarks.landmark)
            
            # Update statistics
            self.update_statistics(gesture)
        else:
            # No hand detected
            if self.last_gesture:
                self.gesture_counts[self.last_gesture] += 1
            self.last_gesture = None
            self.gesture_start_time = None
            self.gesture_duration = 0
        
        return frame, gesture, finger_count
    
    def get_statistics(self):
        """Get gesture statistics"""
        return self.gesture_counts, self.gesture_duration
    
    def close(self):
        """Release resources"""
        self.hands.close()


def draw_info_panel(frame, gesture, finger_count, statistics, duration):
    """Draw information panel with gesture details"""
    h, w, _ = frame.shape
    
    # Semi-transparent overlay
    overlay = frame.copy()
    cv2.rectangle(overlay, (10, 10), (w - 10, 250), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
    
    # Title
    cv2.putText(frame, "GESTURE TESTING MODE", (20, 40),
               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
    
    # Current gesture with color coding
    if gesture:
        color_map = {
            "ONE": (0, 255, 0),
            "TWO": (0, 255, 0),
            "OPEN": (0, 255, 0),
            "CLOSED": (0, 255, 0),
            "THUMBS_UP": (255, 128, 0),
            "THUMBS_DOWN": (255, 128, 0),
            "UNKNOWN": (0, 0, 255)
        }
        color = color_map.get(gesture, (255, 255, 255))
        
        cv2.putText(frame, f"Current: {gesture}", (20, 80),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        
        # Display gesture hold duration
        if duration > 0:
            cv2.putText(frame, f"Hold Time: {duration:.2f}s", (20, 115),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    else:
        cv2.putText(frame, "Current: No hand detected", (20, 80),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (128, 128, 128), 2)
    
    # Finger count
    cv2.putText(frame, f"Fingers Extended: {finger_count}", (20, 150),
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    # Statistics
    y_pos = 185
    cv2.putText(frame, "Detection Count:", (20, y_pos),
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
    
    y_pos += 25
    total = sum(statistics.values())
    for gest, count in statistics.items():
        if gest != "UNKNOWN":
            percentage = (count / total * 100) if total > 0 else 0
            text = f"{gest}: {count} ({percentage:.1f}%)"
            cv2.putText(frame, text, (30, y_pos),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 180), 1)
            y_pos += 20
            if y_pos > h - 30:
                break


def draw_gesture_guide(frame):
    """Draw gesture guide at the bottom"""
    h, w, _ = frame.shape
    
    # Guide box
    overlay = frame.copy()
    cv2.rectangle(overlay, (10, h - 180), (w - 10, h - 10), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
    
    # Guide text
    y = h - 155
    cv2.putText(frame, "GESTURE GUIDE:", (20, y),
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    
    y += 25
    gestures = [
        "☝ ONE: Index finger up (Switch to LED)",
        "✌ TWO: Index & middle up (Switch to Motor)",
        "✋ OPEN: All fingers extended (Turn ON)",
        "✊ CLOSED: Fist (Turn OFF)",
        "👍 THUMBS UP: Hold 2s to increase",
        "👎 THUMBS DOWN: Hold 2s to decrease"
    ]
    
    for i, text in enumerate(gestures):
        if y + i * 22 < h - 20:
            cv2.putText(frame, text, (30, y + i * 22),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)


def main():
    """Main testing loop"""
    print("=" * 60)
    print("GESTURE TESTING PROGRAM")
    print("=" * 60)
    print("\nThis program tests gesture detection accuracy")
    print("Try each gesture and observe the detection")
    print("\nPress 'q' to quit")
    print("Press 'r' to reset statistics")
    print("=" * 60)
    
    # Initialize detector
    detector = HandGestureDetector()
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    if not cap.isOpened():
        print("Error: Could not open camera")
        return
    
    print("\n✓ Camera initialized")
    print("✓ Starting gesture detection...\n")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Flip for mirror view
            frame = cv2.flip(frame, 1)
            
            # Process frame
            processed_frame, gesture, finger_count = detector.process_frame(frame)
            
            # Get statistics
            statistics, duration = detector.get_statistics()
            
            # Draw info panel
            draw_info_panel(processed_frame, gesture, finger_count, statistics, duration)
            
            # Draw gesture guide
            draw_gesture_guide(processed_frame)
            
            # Instructions
            cv2.putText(processed_frame, "Press 'q' to quit | Press 'r' to reset", 
                       (10, processed_frame.shape[0] - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Display frame
            cv2.imshow('Gesture Testing Program', processed_frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                # Reset statistics
                detector.gesture_counts = {k: 0 for k in detector.gesture_counts}
                print("\n✓ Statistics reset")
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    
    finally:
        # Print final statistics
        print("\n" + "=" * 60)
        print("FINAL STATISTICS")
        print("=" * 60)
        statistics, _ = detector.get_statistics()
        total = sum(statistics.values())
        
        for gesture, count in statistics.items():
            if gesture != "UNKNOWN":
                percentage = (count / total * 100) if total > 0 else 0
                print(f"  {gesture:12s}: {count:4d} detections ({percentage:5.1f}%)")
        
        print("=" * 60)
        
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        detector.close()
        print("\n✓ Testing complete")


if __name__ == "__main__":
    main()
