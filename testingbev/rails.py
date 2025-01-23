import time
from adafruit_mcp230xx.mcp23017 import MCP23017
import board
import busio
import digitalio

# Initialize MCP23017
print("Initializing MCP23017 I/O expander...")
i2c = busio.I2C(board.SCL, board.SDA)
mcp = MCP23017(i2c, address=0x26)  # MCP23017 at address 0x24
print("MCP23017 initialized.")

# Define motor pins
motor_pins = {
    "horizontal_1": {"pulse": mcp.get_pin(2), "direction": mcp.get_pin(3)},
    "horizontal_2": {"pulse": mcp.get_pin(4), "direction": mcp.get_pin(5)},
    "gantry": {"pulse": mcp.get_pin(0), "direction": mcp.get_pin(1)}
}

ENABLE_PIN = 6  # Shared Enable Pin for all motors

# Set up MCP23017 pins as outputs
for motor_name, pins in motor_pins.items():
    pins["pulse"].direction = digitalio.Direction.OUTPUT
    pins["direction"].direction = digitalio.Direction.OUTPUT

# Enable Pin Setup
enable_pin = mcp.get_pin(ENABLE_PIN)
enable_pin.direction = digitalio.Direction.OUTPUT

# Function to move a single stepper motor
def move_stepper(motor_pins, steps, direction):
    # Set the direction pin
    motor_pins['direction'].value = True if direction == 'forward' else False

    # Enable the motor
    enable_pin.value = False  # Active low to enable

    # Pulse the motor for the given number of steps
    for step in range(steps):
        motor_pins['pulse'].value = True
        time.sleep(0.00025)  # Adjust pulse width as needed
        motor_pins['pulse'].value = False
        time.sleep(0.00025)

    # Disable the motor after movement
    enable_pin.value = True  # Active high to disable

# Function to move two motors synchronously
def move_horizontal_synchronously(motor_pins_1, motor_pins_2, steps, direction):
    enable_pin.value = False  # Enable all motors
    motor_pins_1['direction'].value = True if direction == 'forward' else False
    motor_pins_2['direction'].value = True if direction == 'forward' else False

    for step in range(steps):
        motor_pins_1['pulse'].value = True
        motor_pins_2['pulse'].value = True
        time.sleep(0.00001)
        motor_pins_1['pulse'].value = False
        motor_pins_2['pulse'].value = False
        time.sleep(0.00001)

    enable_pin.value = True  # Disable all motors

# Function to move three motors synchronously
def move_three_motors_synchronously(motor_pins_1, motor_pins_2, motor_pins_3, steps_1, steps_2, steps_3, direction):
    enable_pin.value = False

    motor_pins_1['direction'].value = True if direction == 'forward' else False
    motor_pins_2['direction'].value = True if direction == 'forward' else False
    motor_pins_3['direction'].value = True if direction == 'forward' else False

    for step in range(max(steps_1, steps_2, steps_3)):
        if step < steps_1:
            motor_pins_1['pulse'].value = True
        if step < steps_2:
            motor_pins_2['pulse'].value = True
        if step < steps_3:
            motor_pins_3['pulse'].value = True

        time.sleep(0.00001)

        if step < steps_1:
            motor_pins_1['pulse'].value = False
        if step < steps_2:
            motor_pins_2['pulse'].value = False
        if step < steps_3:
            motor_pins_3['pulse'].value = False

        time.sleep(0.00001)

    enable_pin.value = True  # Disable all motors

# Main control loop
if __name__ == "__main__":
    try:
        while True:
            print("\nMotor Control Menu:")
            print("1. Move horizontal_1 motor")
            print("2. Move horizontal_2 motor")
            print("3. Move gantry motor")
            print("4. Move horizontal_1 and horizontal_2 synchronously")
            print("5. Move all three motors synchronously")
            print("6. Exit")
            choice = int(input("Enter your choice: "))

            if choice == 1:
                steps = int(input("Enter number of steps: "))
                direction = input("Enter direction (forward/reverse): ").strip().lower()
                move_stepper(motor_pins["horizontal_1"], steps, direction)

            elif choice == 2:
                steps = int(input("Enter number of steps: "))
                direction = input("Enter direction (forward/reverse): ").strip().lower()
                move_stepper(motor_pins["horizontal_2"], steps, direction)

            elif choice == 3:
                steps = int(input("Enter number of steps: "))
                direction = input("Enter direction (forward/reverse): ").strip().lower()
                move_stepper(motor_pins["gantry"], steps, direction)

            elif choice == 4:
                steps = int(input("Enter number of steps: "))
                direction = input("Enter direction (forward/reverse): ").strip().lower()
                move_horizontal_synchronously(motor_pins["horizontal_1"], motor_pins["horizontal_2"], steps, direction)

            elif choice == 5:
                steps_1 = int(input("Enter steps for horizontal_1: "))
                steps_2 = int(input("Enter steps for horizontal_2: "))
                steps_3 = int(input("Enter steps for gantry: "))
                direction = input("Enter direction (forward/reverse): ").strip().lower()
                move_three_motors_synchronously(
                    motor_pins["horizontal_1"], 
                    motor_pins["horizontal_2"], 
                    motor_pins["gantry"], 
                    steps_1, steps_2, steps_3, direction)

            elif choice == 6:
                print("Exiting...")
                break

            else:
                print("Invalid choice. Please try again.")

    except Exception as e:
        print(f"Error occurred: {str(e)}")
