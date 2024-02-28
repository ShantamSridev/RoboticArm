import serial
import time

# Change 'COM3' to the COM port to which your Arduino is connected
arduino = serial.Serial(port='COM5', baudrate=9600, timeout=.1)

def write_servos(angles):
    """
    Send a command to the Arduino to move servos to the specified angles.
    Angles should be a dictionary where key is the servo number (0-4)
    and value is the angle (0-180).
    """
    command = ','.join(f'S{i}:{angles[i]}' for i in angles)
    command += '\n'  # Add newline to signal end of command
    arduino.write(bytes(command, 'utf-8'))

def open_fingers():
    open = {0: 180, 1: 180, 2: 180, 3: 180, 4: 180}
    return open

def close_fingers():
    close = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
    return close

def main():
    # Example: move servo 0 to 90 degrees, servo 1 to 45 degrees, etc.

    # Thumb is 0
    # ring is 1
    # Middle is 2
    # index is 3
    # pinky is 4
    servo_positions = open_fingers()
    write_servos(servo_positions)

    time.sleep(2)  # Wait for the movement to complete

if __name__ == "__main__":
    main()
