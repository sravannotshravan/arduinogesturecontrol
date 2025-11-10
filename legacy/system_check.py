#!/usr/bin/env python3
"""
System Check - Verify installation and dependencies
Tests that all required packages are installed and working
"""

import sys
import os

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def check_python_version():
    """Check Python version"""
    print("\n📌 Python Version:")
    version = sys.version_info
    print(f"   Version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 8:
        print("   ✅ Python version is compatible (3.8+)")
        return True
    else:
        print("   ❌ Python 3.8+ required")
        return False

def check_package(package_name, import_name=None):
    """Check if a package is installed and importable"""
    if import_name is None:
        import_name = package_name
    
    print(f"\n📦 Checking {package_name}...")
    try:
        module = __import__(import_name)
        version = getattr(module, '__version__', 'Unknown')
        print(f"   ✅ {package_name} installed (version: {version})")
        return True
    except ImportError as e:
        print(f"   ❌ {package_name} not found")
        print(f"   Install with: pip install {package_name}")
        return False

def check_camera():
    """Check if camera is accessible"""
    print("\n📷 Checking Camera Access...")
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                h, w = frame.shape[:2]
                print(f"   ✅ Camera accessible (Resolution: {w}x{h})")
                cap.release()
                return True
            else:
                print("   ⚠️  Camera opened but can't read frames")
                cap.release()
                return False
        else:
            print("   ❌ Cannot open camera")
            print("   Make sure camera is connected and not in use")
            return False
    except Exception as e:
        print(f"   ❌ Error accessing camera: {e}")
        return False

def check_mediapipe():
    """Check MediaPipe hands solution"""
    print("\n🤚 Checking MediaPipe Hands...")
    try:
        import mediapipe as mp
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(
            static_image_mode=True,
            max_num_hands=1,
            min_detection_confidence=0.5
        )
        print("   ✅ MediaPipe Hands initialized successfully")
        hands.close()
        return True
    except Exception as e:
        print(f"   ❌ Error initializing MediaPipe: {e}")
        return False

def check_gpio():
    """Check if RPi.GPIO is available (optional for simulation)"""
    print("\n🔌 Checking RPi.GPIO (Raspberry Pi only)...")
    try:
        import RPi.GPIO as GPIO
        print(f"   ✅ RPi.GPIO installed (version: {GPIO.VERSION})")
        print("   ✅ Running on Raspberry Pi - Hardware control available")
        return True
    except ImportError:
        print("   ⚠️  RPi.GPIO not found (normal on non-Raspberry Pi systems)")
        print("   ℹ️  Simulation and testing modes will work")
        return None  # Not an error, just not on Pi

def check_files():
    """Check if all program files exist"""
    print("\n📄 Checking Program Files...")
    
    required_files = [
        "gesture_control_system.py",
        "gesture_control_simulation.py",
        "gesture_testing.py",
        "hand_gesture_detection.py",
        "requirements.txt"
    ]
    
    all_exist = True
    for filename in required_files:
        if os.path.exists(filename):
            print(f"   ✅ {filename}")
        else:
            print(f"   ❌ {filename} - MISSING")
            all_exist = False
    
    return all_exist

def print_summary(results):
    """Print summary of checks"""
    print_header("SUMMARY")
    
    passed = sum(1 for r in results.values() if r is True)
    failed = sum(1 for r in results.values() if r is False)
    optional = sum(1 for r in results.values() if r is None)
    
    print(f"\n   ✅ Passed:   {passed}")
    print(f"   ❌ Failed:   {failed}")
    print(f"   ⚠️  Optional: {optional}")
    
    print("\n" + "-" * 60)
    
    if failed == 0:
        print("\n   🎉 All checks passed! System is ready to use.")
        
        if results.get('gpio') is None:
            print("\n   💡 You're on a non-Raspberry Pi system.")
            print("      You can use:")
            print("      • gesture_control_simulation.py")
            print("      • gesture_testing.py")
        else:
            print("\n   💡 You're on a Raspberry Pi!")
            print("      You can use all programs:")
            print("      • gesture_control_system.py (hardware)")
            print("      • gesture_control_simulation.py")
            print("      • gesture_testing.py")
    else:
        print("\n   ⚠️  Some checks failed. Install missing packages:")
        print("      pip install opencv-python mediapipe numpy")
        if results.get('gpio') is False:
            print("      pip install RPi.GPIO  # On Raspberry Pi only")

def main():
    """Main system check"""
    print_header("GESTURE CONTROL SYSTEM - SYSTEM CHECK")
    
    print("\nThis script verifies that all dependencies are installed")
    print("and the system is ready to run the gesture control programs.")
    
    results = {}
    
    # Check Python version
    results['python'] = check_python_version()
    
    # Check required packages
    results['opencv'] = check_package('opencv-python', 'cv2')
    results['mediapipe'] = check_package('mediapipe')
    results['numpy'] = check_package('numpy')
    
    # Check optional GPIO (only on Raspberry Pi)
    results['gpio'] = check_gpio()
    
    # Check MediaPipe functionality
    if results['mediapipe'] and results['opencv']:
        results['mediapipe_hands'] = check_mediapipe()
    else:
        results['mediapipe_hands'] = False
    
    # Check camera access
    if results['opencv']:
        results['camera'] = check_camera()
    else:
        results['camera'] = False
    
    # Check program files
    results['files'] = check_files()
    
    # Print summary
    print_summary(results)
    
    # Exit code
    failed = sum(1 for r in results.values() if r is False)
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Check interrupted by user")
        sys.exit(1)
