#!/usr/bin/env python3
"""
Gesture Control SERVER - Runs on Raspberry Pi
Receives control commands from laptop client and controls hardware (LED & Servo Motor)

This program:
1. Listens for connections from laptop client
2. Receives gesture control commands over network
3. Controls LED and servo motor via GPIO
4. Sends status updates back to client
"""

import socket
import json
import time
import threading
try:
    import RPi.GPIO as GPIO
except ImportError:
    print("Warning: RPi.GPIO not available. Running in simulation mode.")
    GPIO = None


class DeviceController:
    """Controls LED and Servo Motor via GPIO"""
    
    # GPIO Pin assignments
    LED_PIN = 18      # GPIO 18 (Physical Pin 12)
    SERVO_PIN = 13    # GPIO 13 (Physical Pin 33)
    
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
        
        # Setup Servo with PWM (50 Hz)
        GPIO.setup(self.SERVO_PIN, GPIO.OUT)
        self.servo_pwm = GPIO.PWM(self.SERVO_PIN, 50)
        self.servo_pwm.start(7.5)
        
        # State variables
        self.led_level = 0
        self.motor_level = 0
        self.led_on = False
        self.motor_on = False
        self.mode = "LED"
        
        print(f"✓ GPIO Initialized")
        print(f"  LED Pin: GPIO {self.LED_PIN} (Physical Pin 12)")
        print(f"  Servo Pin: GPIO {self.SERVO_PIN} (Physical Pin 33)")
    
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
        """Set servo motor rotation speed (0-5)"""
        self.motor_level = max(0, min(5, level))
        if self.motor_on and self.motor_level > 0:
            base_stop = 7.5
            max_forward = 12.0
            speed_range = max_forward - base_stop
            duty_cycle = base_stop + (self.motor_level / 5.0) * speed_range
            
            self.servo_pwm.ChangeDutyCycle(duty_cycle)
            speed_percent = (self.motor_level / 5.0) * 100
            print(f"⚙️  Servo Speed: {self.motor_level}/5 ({speed_percent:.0f}%)")
        else:
            self.servo_pwm.ChangeDutyCycle(7.5)
            time.sleep(0.1)
            self.servo_pwm.ChangeDutyCycle(0)
    
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
        self.led_pwm.ChangeDutyCycle(0)
        print("💡 LED: OFF")
    
    def motor_turn_on(self):
        """Turn motor on"""
        self.motor_on = True
        if self.motor_level == 0:
            self.motor_level = 3
        self.set_servo_speed(self.motor_level)
        print("⚙️  Motor: ON")
    
    def motor_turn_off(self):
        """Turn motor off"""
        self.motor_on = False
        self.servo_pwm.ChangeDutyCycle(7.5)
        time.sleep(0.1)
        self.servo_pwm.ChangeDutyCycle(0)
        print("⚙️  Motor: OFF")
    
    def increase_led(self):
        """Increase LED brightness"""
        if self.led_on:
            self.set_led_brightness(self.led_level + 1)
    
    def decrease_led(self):
        """Decrease LED brightness"""
        if self.led_on:
            self.set_led_brightness(self.led_level - 1)
    
    def increase_motor(self):
        """Increase motor speed"""
        if self.motor_on:
            self.set_servo_speed(self.motor_level + 1)
    
    def decrease_motor(self):
        """Decrease motor speed"""
        if self.motor_on:
            self.set_servo_speed(self.motor_level - 1)
    
    def get_status(self):
        """Get current device status"""
        return {
            'mode': self.mode,
            'led': {
                'on': self.led_on,
                'level': self.led_level
            },
            'motor': {
                'on': self.motor_on,
                'level': self.motor_level
            }
        }
    
    def cleanup(self):
        """Cleanup GPIO"""
        self.led_pwm.stop()
        self.servo_pwm.stop()
        GPIO.cleanup()
        print("✓ GPIO Cleaned up")


class NetworkServer:
    """Handles network communication with laptop client"""
    
    def __init__(self, controller, port=5000):
        self.controller = controller
        self.port = port
        self.server_socket = None
        self.client_socket = None
        self.client_address = None
        self.running = False
        self.status_thread = None
    
    def start(self):
        """Start the server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('0.0.0.0', self.port))
            self.server_socket.listen(1)
            self.running = True
            
            # Get local IP
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            
            print(f"\n✓ Server started on {local_ip}:{self.port}")
            print(f"Waiting for client connection...")
            print(f"\nOn your laptop, run:")
            print(f"  python gesture_control_client.py")
            print(f"  Enter IP: {local_ip}")
            
            return True
        except Exception as e:
            print(f"✗ Server start failed: {e}")
            return False
    
    def wait_for_client(self):
        """Wait for client connection"""
        try:
            self.client_socket, self.client_address = self.server_socket.accept()
            print(f"\n✓ Client connected from {self.client_address[0]}")
            
            # Start status update thread
            self.status_thread = threading.Thread(target=self._send_status_updates, daemon=True)
            self.status_thread.start()
            
            return True
        except Exception as e:
            print(f"✗ Client connection failed: {e}")
            return False
    
    def _send_status_updates(self):
        """Periodically send status updates to client"""
        while self.running and self.client_socket:
            try:
                status = self.controller.get_status()
                message = json.dumps(status) + '\n'
                self.client_socket.sendall(message.encode('utf-8'))
                time.sleep(0.1)  # Send updates 10 times per second
            except:
                break
    
    def handle_commands(self):
        """Handle incoming commands from client"""
        buffer = ""
        
        try:
            while self.running:
                data = self.client_socket.recv(1024)
                if not data:
                    print("\n✗ Client disconnected")
                    break
                
                buffer += data.decode('utf-8')
                
                # Process complete messages (newline-separated)
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line.strip():
                        self._process_command(line)
        
        except Exception as e:
            print(f"\n✗ Connection error: {e}")
        
        finally:
            if self.client_socket:
                self.client_socket.close()
                self.client_socket = None
    
    def _process_command(self, message):
        """Process a single command"""
        try:
            command = json.loads(message)
            cmd_type = command.get('type')
            data = command.get('data', {})
            
            if cmd_type == 'mode':
                self.controller.mode = data.get('mode', 'LED')
                print(f"\n📍 Mode changed to: {self.controller.mode}")
            
            elif cmd_type == 'turn_on':
                if self.controller.mode == 'LED':
                    self.controller.led_turn_on()
                else:
                    self.controller.motor_turn_on()
            
            elif cmd_type == 'turn_off':
                if self.controller.mode == 'LED':
                    self.controller.led_turn_off()
                else:
                    self.controller.motor_turn_off()
            
            elif cmd_type == 'increase':
                if self.controller.mode == 'LED':
                    self.controller.increase_led()
                else:
                    self.controller.increase_motor()
            
            elif cmd_type == 'decrease':
                if self.controller.mode == 'LED':
                    self.controller.decrease_led()
                else:
                    self.controller.decrease_motor()
            
            else:
                print(f"Unknown command: {cmd_type}")
        
        except Exception as e:
            print(f"Command processing error: {e}")
    
    def stop(self):
        """Stop the server"""
        self.running = False
        if self.client_socket:
            self.client_socket.close()
        if self.server_socket:
            self.server_socket.close()
        print("\n✓ Server stopped")


def main():
    """Main server loop"""
    print("=" * 60)
    print("GESTURE CONTROL SERVER - RASPBERRY PI")
    print("=" * 60)
    print("\nThis program receives gesture commands from laptop")
    print("and controls LED and servo motor hardware")
    print("\nPress Ctrl+C to quit")
    print("=" * 60)
    
    # Initialize controller
    try:
        controller = DeviceController()
    except RuntimeError as e:
        print(f"\nError: {e}")
        print("Make sure you're running on Raspberry Pi with GPIO access")
        return
    
    # Initialize server
    server = NetworkServer(controller)
    
    if not server.start():
        return
    
    try:
        while True:
            # Wait for client connection
            if server.wait_for_client():
                # Handle commands until client disconnects
                server.handle_commands()
                print("\nWaiting for new client connection...")
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    
    finally:
        # Cleanup
        server.stop()
        controller.cleanup()
        print("\n✓ Server shutdown complete")


if __name__ == "__main__":
    main()
