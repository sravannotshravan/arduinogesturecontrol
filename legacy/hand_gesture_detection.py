#!/usr/bin/env python3
"""
Hand Gesture Detection for Raspberry Pi 5
Detects: Number 1, Number 2, Open Hand, Closed Hand (Fist), Thumbs Up, Thumbs Down
"""

import cv2
import mediapipe as mp
import math

class HandGestureDetector:
    def __init__(self):
        # Initialize MediaPipe Hand solution
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
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
        mcp = landmarks[finger_pip_id - 1]
        
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
        ring_tip = landmarks[16]
        pinky_tip = landmarks[20]
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
                    return "THUMBS UP"
        
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
                    return "THUMBS DOWN"
        
        # Number 1 Detection (only index finger up, thumb closed)
        if 8 in extended_fingers and count == 1 and not thumb_extended:
            return "NUMBER 1"
        
        # Number 2 Detection (index and middle finger up)
        if 8 in extended_fingers and 12 in extended_fingers and count == 2:
            # Check if fingers are separated (peace sign)
            distance = self.calculate_distance(index_tip, middle_tip)
            if distance > 0.05:
                return "NUMBER 2"
        
        # Open Hand Detection (all fingers extended including thumb)
        if count >= 4 and thumb_extended:
            return "OPEN HAND"
        
        # Closed Hand/Fist Detection - all fingers closed INCLUDING thumb
        if count == 0:
            # Check that all fingertips are close to palm
            avg_distance = sum([
                self.calculate_distance(palm_center, landmarks[tip])
                for tip in [4, 8, 12, 16, 20]  # Include thumb
            ]) / 5
            
            if avg_distance < 0.12:
                return "CLOSED HAND (FIST)"
        
        return "UNKNOWN"
    
    def process_frame(self, frame):
        """Process a single frame and detect gestures"""
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame
        results = self.hands.process(rgb_frame)
        
        gestures = []
        
        # Draw hand landmarks and detect gestures
        if results.multi_hand_landmarks:
            for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # Draw hand landmarks
                self.mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS
                )
                
                # Detect gesture
                gesture = self.detect_gesture(hand_landmarks.landmark)
                gestures.append(gesture)
                
                # Display gesture name on frame
                h, w, _ = frame.shape
                hand_label_pos = (int(hand_landmarks.landmark[0].x * w), 
                                 int(hand_landmarks.landmark[0].y * h) - 20)
                
                cv2.putText(frame, gesture, hand_label_pos,
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        return frame, gestures
    
    def close(self):
        """Release resources"""
        self.hands.close()


def main():
    """Main function to run the gesture detection"""
    print("Starting Hand Gesture Detection...")
    print("Detecting: Number 1, Number 2, Open Hand, Closed Hand, Thumbs Up, Thumbs Down")
    print("Press 'q' to quit")
    
    # Initialize camera (Raspberry Pi Camera)
    # For Raspberry Pi Camera Module, use index 0
    cap = cv2.VideoCapture(0)
    
    # Set camera resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    if not cap.isOpened():
        print("Error: Could not open camera")
        return
    
    # Initialize gesture detector
    detector = HandGestureDetector()
    
    try:
        while True:
            # Read frame from camera
            ret, frame = cap.read()
            
            if not ret:
                print("Error: Could not read frame")
                break
            
            # Flip frame horizontally for mirror view
            frame = cv2.flip(frame, 1)
            
            # Process frame and detect gestures
            processed_frame, gestures = detector.process_frame(frame)
            
            # Display instructions
            cv2.putText(processed_frame, "Press 'q' to quit", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Print detected gestures to console
            if gestures:
                print(f"Detected: {', '.join(gestures)}")
            
            # Display the frame
            cv2.imshow('Hand Gesture Detection - Raspberry Pi 5', processed_frame)
            
            # Check for quit command
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    
    finally:
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        detector.close()
        print("Gesture detection stopped")


if __name__ == "__main__":
    main()
