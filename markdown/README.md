# Hand Gesture Detection for Raspberry Pi 5

This project detects hand gestures using the Raspberry Pi 5 camera module and MediaPipe.

## Detected Gestures

- **Number 1**: Index finger extended
- **Number 2**: Index and middle fingers extended (peace sign)
- **Open Hand**: All fingers extended
- **Closed Hand (Fist)**: All fingers closed
- **Thumbs Up**: Thumb pointing up
- **Thumbs Down**: Thumb pointing down

## Installation

### Prerequisites

1. Raspberry Pi 5 with Raspberry Pi OS (64-bit recommended)
2. Camera module connected to the camera port
3. Python 3.9 or higher

### Setup Instructions

1. **Enable the camera** (if not already enabled):
   ```bash
   sudo raspi-config
   # Navigate to Interface Options -> Camera -> Enable
   ```

2. **Update system packages**:
   ```bash
   sudo apt update
   sudo apt upgrade -y
   ```

3. **Install system dependencies**:
   ```bash
   sudo apt install -y python3-pip python3-opencv
   sudo apt install -y libatlas-base-dev libhdf5-dev libhdf5-serial-dev
   sudo apt install -y libharfbuzz0b libwebp7 libtiff5 libjasper1
   sudo apt install -y libilmbase25 libopenexr25 libgstreamer1.0-0
   sudo apt install -y libavcodec58 libavformat58 libswscale5
   sudo apt install -y libqt5gui5 libqt5webkit5 libqt5test5
   ```

4. **Install Python packages**:
   ```bash
   pip3 install -r requirements.txt
   ```

   Or install individually:
   ```bash
   pip3 install opencv-python mediapipe numpy
   ```

## Usage

1. **Run the script**:
   ```bash
   python3 hand_gesture_detection.py
   ```

2. **Controls**:
   - Press `q` to quit the application
   - Show your hand to the camera to detect gestures
   - The detected gesture will be displayed on the screen and printed to the console

## Troubleshooting

### Camera not detected
- Check if the camera is properly connected to the camera port
- Enable the camera using `sudo raspi-config`
- Test the camera with: `libcamera-hello`

### ImportError for cv2
- Make sure OpenCV is properly installed
- Try: `pip3 install opencv-python --upgrade`

### MediaPipe installation issues
- For Raspberry Pi, you may need to install from source or use a compatible wheel
- Check MediaPipe's compatibility with your ARM architecture

### Performance issues
- Reduce camera resolution in the script (lines 142-143)
- Lower the `min_detection_confidence` parameter
- Ensure adequate lighting for better detection

## How It Works

1. **Camera Capture**: Captures video frames from the Raspberry Pi camera
2. **Hand Detection**: Uses MediaPipe to detect and track hand landmarks (21 points per hand)
3. **Gesture Recognition**: Analyzes finger positions and angles to identify specific gestures
4. **Visual Feedback**: Draws hand landmarks and displays the detected gesture on screen

## Customization

You can modify the gesture detection logic in the `detect_gesture()` method to add more gestures or adjust sensitivity by changing:
- `min_detection_confidence` (line 16): Lower for easier detection, higher for accuracy
- `min_tracking_confidence` (line 17): Smoothness of tracking
- Distance thresholds in gesture detection logic

## License

This project is open source and available for educational purposes.
