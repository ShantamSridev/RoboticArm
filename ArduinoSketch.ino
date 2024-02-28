#include <Servo.h>

// Define the number of servos
const int numServos = 5;

// Create Servo objects
Servo servos[numServos];

// Define the pins where the servos are connected
int servoPins[numServos] = {0, 1, 2, 3, 4}; // Change these pins according to your setup

void setup() {
    // Start serial communication
    Serial.begin(9600);
    
    // Attach each servo to its pin
    for(int i = 0; i < numServos; i++) {
        servos[i].attach(servoPins[i]);
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
    // Expected command format "S0:90,S1:45,S2:180,S3:90,S4:10"
    for (int i = 0; i < numServos; i++) {
        // Construct the search term for current servo (e.g., "S0:", "S1:", etc.)
        String searchTerm = "S" + String(i) + ":";
        int index = command.indexOf(searchTerm);

        if (index != -1) { // If the term is found
            int start = index + searchTerm.length();
            int end = command.indexOf(',', start);
            if (end == -1) end = command.length(); // If this is the last command
            int angle = command.substring(start, end).toInt(); // Get the angle value
            servos[i].write(angle); // Set the servo position
        }
    }
}
