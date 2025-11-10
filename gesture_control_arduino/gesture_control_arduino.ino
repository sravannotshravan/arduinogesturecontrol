#include <Servo.h>

const int LED_PIN = 11; // moved from 9 to 11 to avoid Timer1 conflict
const int SERVO_PIN = 8;

Servo motor;

String currentMode = "LED";
bool ledOn = false;
bool motorOn = false;
int ledLevel = 3;      // 0..5
int motorLevel = 3;    // 0..5

String inputString = "";
boolean stringComplete = false;

void setup() {
  Serial.begin(115200);
  while (!Serial) {}
  pinMode(LED_PIN, OUTPUT);
  analogWrite(LED_PIN, 0);
  motor.attach(SERVO_PIN);
  motor.write(90);
  inputString.reserve(64);
  Serial.println("READY:Arduino Gesture Control System");
  Serial.println("INFO:LED=Pin11, Servo=Pin8");
  Serial.flush();
}

void loop() {
  if (stringComplete) {
    processCommand(inputString);
    inputString = "";
    stringComplete = false;
  }
}

void serialEvent() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    if (inChar == '\n') {
      stringComplete = true;
    } else if (inChar != '\r') {
      inputString += inChar;
    }
  }
}

void processCommand(String command) {
  command.trim();
  if (command.startsWith("MODE:")) {
    String mode = command.substring(5);
    mode.toUpperCase();
    if (mode == "LED" || mode == "MOTOR") {
      currentMode = mode;
      Serial.print("MODE:");
      Serial.println(currentMode);
    }
  }
  else if (command.startsWith("LED:")) {
    String action = command.substring(4);
    action.toUpperCase();
    if (action == "ON") ledTurnOn();
    else if (action == "OFF") ledTurnOff();
    else if (action == "UP") ledIncrease();
    else if (action == "DOWN") ledDecrease();
  }
  else if (command.startsWith("MOTOR:")) {
    String action = command.substring(6);
    action.toUpperCase();
    if (action == "ON") motorTurnOn();
    else if (action == "OFF") motorTurnOff();
    else if (action == "UP") motorIncrease();
    else if (action == "DOWN") motorDecrease();
  }
  else if (command == "STATUS") {
    sendStatus();
  }
  else if (command == "STOP") {
    emergencyStop();
  }
}

void ledTurnOn() {
  ledOn = true;
  setLedBrightness(ledLevel);
  Serial.println("LED:ON");
}

void ledTurnOff() {
  ledOn = false;
  analogWrite(LED_PIN, 0);
  Serial.println("LED:OFF");
}

void ledIncrease() {
  if (ledLevel < 5) {
    ledLevel++;
    setLedBrightness(ledLevel);
  }
  Serial.print("LED:LEVEL:");
  Serial.print(ledLevel);
  Serial.print(":");
  Serial.println(map(ledLevel, 0, 5, 0, 100));
}

void ledDecrease() {
  if (ledLevel > 0) {
    ledLevel--;
    setLedBrightness(ledLevel);
  }
  Serial.print("LED:LEVEL:");
  Serial.print(ledLevel);
  Serial.print(":");
  Serial.println(map(ledLevel, 0, 5, 0, 100));
}

void setLedBrightness(int level) {
  level = constrain(level, 0, 5);
  int pwmValue = map(level, 0, 5, 0, 255);
  pwmValue = constrain(pwmValue, 0, 255);
  if (ledOn) {
    analogWrite(LED_PIN, pwmValue);
  } else {
    analogWrite(LED_PIN, 0);
  }
  int percentage = map(level, 0, 5, 0, 100);
  Serial.print("LED:SET:");
  Serial.print(level);
  Serial.print(":");
  Serial.println(percentage);
}

void motorTurnOn() {
  motorOn = true;
  Serial.println("MOTOR: Swinging back and forth");
  for (int angle = 0; angle <= 180; angle += 2) {
    motor.write(angle);
    delay(15);
  }
  for (int angle = 180; angle >= 0; angle -= 2) {
    motor.write(angle);
    delay(15);
  }
}

void motorTurnOff() {
  motorOn = false;
  motor.write(90);
  Serial.println("MOTOR:OFF");
}

void motorIncrease() {
  if (motorOn && motorLevel < 5) {
    motorLevel++;
    Serial.print("MOTOR:LEVEL:");
    Serial.println(motorLevel);
  }
}

void motorDecrease() {
  if (motorOn && motorLevel > 0) {
    motorLevel--;
    Serial.print("MOTOR:LEVEL:");
    Serial.println(motorLevel);
  }
}

void setMotorSpeed(int level) {
  if (motorOn) {
    motor.write(180);
  }
}

void sendStatus() {
  Serial.print("STATUS:");
  Serial.print(currentMode);
  Serial.print(",");
  Serial.print(ledOn ? "ON" : "OFF");
  Serial.print(",");
  Serial.print(ledLevel);
  Serial.print(",");
  Serial.print(motorOn ? "ON" : "OFF");
  Serial.print(",");
  Serial.println(motorLevel);
}

void emergencyStop() {
  // Turn off LED
  ledOn = false;
  analogWrite(LED_PIN, 0);
  
  // Stop motor
  motorOn = false;
  motor.write(90);
  
  // Reset levels to default
  ledLevel = 3;
  motorLevel = 3;
  
  Serial.println("STOP:ALL_DEVICES_OFF");
  Serial.println("LED:OFF");
  Serial.println("MOTOR:OFF");
}
