#include <Servo.h>

// Define the number of servos
const int numServos = 5;

// Create Servo objects
Servo servos[numServos];

// Define the pins where the servos are connected
int servoPins[numServos] = {0, 1, 2, 3, 4}; // Change these pins according to your setup

unsigned long DelayDuration = 700;
unsigned long PreviousTime = 0;
unsigned long CurrentTime = 0;

void setup() {
    // Start serial communication
    Serial.begin(9600);
    
    // Attach each servo to its pin
    for(int i = 0; i < numServos; i++) {
        servos[i].attach(servoPins[i]);
    }

    for (int i = 0; i < numServos; i++) {
            servos[i].write(180); // Set the servo position
        }
}

void loop() {
    // Check if data is available to read
    if (Serial.available() > 0) {
        String data = Serial.readStringUntil('\n'); // Read the incoming data as string until newline
        controlServos(data);
    }
}

void controlServos(String command) {
    // Decode the incoming command and store it as a dictionary
    int servoPositions[numServos];
    for (int i = 0; i < numServos; i++) {
        // Construct the search term for the current servo (e.g., "S0:", "S1:", etc.)
        String searchTerm = "S" + String(i) + ":";
        int index = command.indexOf(searchTerm);

        if (index != -1) { // If the term is found
            int start = index + searchTerm.length();
            int end = command.indexOf(',', start);
            if (end == -1) end = command.length(); // If this is the last command
            servoPositions[i] = command.substring(start, end).toInt(); // Get the angle value
        }
    }
    
    CurrentTime = millis();
    
    if ((CurrentTime-PreviousTime)>DelayDuration) {
        for (int i = 0; i < numServos; i++) {
            servos[i].write(servoPositions[i]); // Set the servo position
        }
        // Introduce a delay without blocking the code execution
        PreviousTime = millis();
    }
}
