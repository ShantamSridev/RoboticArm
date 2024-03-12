#include <Servo.h>

#define SWITCH_PIN 6
#define NUM_SERVOS 5

Servo servos[NUM_SERVOS];
int servoAngles[NUM_SERVOS] = {0, 0, 0, 0, 0};
bool switchState = false;
bool lastSwitchState = false;

void setup() {
  for (int i = 0; i < NUM_SERVOS; i++) {
    servos[i].attach(i);
  }
  pinMode(SWITCH_PIN, INPUT_PULLUP);
}

void loop() {
  switchState = digitalRead(SWITCH_PIN);

  if (switchState != lastSwitchState && switchState == LOW) {
    // Switch was pressed, change servo angles
    for (int i = 0; i < NUM_SERVOS; i++) {
      if (servoAngles[i] == 0) {
        servos[i].write(180); // Set servo to max position
        servoAngles[i] = 180;
      } else {
        servos[i].write(0); // Set servo to min position
        servoAngles[i] = 0;
      }
    }
    delay(200); // Debounce delay
  }

  lastSwitchState = switchState;
}
