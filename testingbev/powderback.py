import time
import RPi.GPIO as GPIO
from adafruit_mcp230xx.mcp23017 import MCP23017
import busio
import board
import digitalio

# Set up I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize MCP23017
mcp = MCP23017(i2c, address=0x24)  

# Define motor pins using MCP23017 GPIO pins (16 total pins available)
MOTOR_PINS = {
    "horizontal_1": {"pulse": mcp.get_pin(2), "direction": mcp.get_pin(3)},
    "horizontal_2": {"pulse": mcp.get_pin(4), "direction": mcp.get_pin(5)},
    "gantry": {"pulse": mcp.get_pin(0), "direction": mcp.get_pin(1)}
}

# Shared Enable Pin for all motors (You can use any GPIO pin or MCP23017 pin for the enable)
ENABLE_PIN = mcp.get_pin(6)  # Example shared enable pin for all motors

# Initialize direction for all motors (set permanent direction)
PERMANENT_DIRECTION = {
    "horizontal_1": True,  # True for forward, False for reverse
    "horizontal_2": True,  # True for forward, False for reverse
    "gantry": False,        # True for forward, False for reverse
}

# Set the pin direction (input or output) for all motor pins
ENABLE_PIN.direction = digitalio.Direction.OUTPUT
for motor_name, motor in MOTOR_PINS.items():
    motor["pulse"].direction = digitalio.Direction.OUTPUT
    motor["direction"].direction = digitalio.Direction.OUTPUT
    motor["direction"].value = PERMANENT_DIRECTION[motor_name]  # Set permanent direction


# Function to enable or disable motors
def enable_motors(enable=True):
    if enable:
        ENABLE_PIN.value = False  # Enable motors (LOW)
    else:
        ENABLE_PIN.value = True  # Disable motors (HIGH)

# Synchronous movement of horizontal motors
def move_horizontal_synchronously(motor_pins_1, motor_pins_2, steps, direction):
    enable_motors(True)  # Enable motors
    motor_pins_1["direction"].value = True if direction == 'forward' else False
    motor_pins_2["direction"].value = True if direction == 'forward' else False

    for step in range(steps):
        motor_pins_1["pulse"].value = True
        motor_pins_2["pulse"].value = True
        time.sleep(0.00001)
        motor_pins_1["pulse"].value = False
        motor_pins_2["pulse"].value = False
        time.sleep(0.00001)

    enable_motors(False)  # Disable motors

# Function to move three motors synchronously
def move_three_motors_synchronously(motor_pins_1, motor_pins_2, motor_pins_3, steps_1, steps_2, steps_3, direction):
    enable_motors(True)  # Enable motors

    motor_pins_1["direction"].value = True if direction == 'forward' else False
    motor_pins_2["direction"].value = True if direction == 'forward' else False
    motor_pins_3["direction"].value = True if direction == 'forward' else False

    for step in range(max(steps_1, steps_2, steps_3)):
        if step < steps_1:
            motor_pins_1["pulse"].value = True
        if step < steps_2:
            motor_pins_2["pulse"].value = True
        if step < steps_3:
            motor_pins_3["pulse"].value = True

        time.sleep(0.00001)

        if step < steps_1:
            motor_pins_1["pulse"].value = False
        if step < steps_2:
            motor_pins_2["pulse"].value = False
        if step < steps_3:
            motor_pins_3["pulse"].value = False

        time.sleep(0.00001)

    enable_motors(False)  # Disable motors

# Stepper motor control for individual motors
def move_stepper(motor_pins, steps, direction):
    enable_motors(True)  # Enable motors
    motor_pins["direction"].value = True if direction == 'forward' else False
    for step in range(steps):
        motor_pins["pulse"].value = True
        time.sleep(0.00001)
        motor_pins["pulse"].value = False
        time.sleep(0.00001)
    enable_motors(False)  # Disable motors

# Function to move gantry to a specific position
def move_gantry_to_position(flavor_position):
    gantry_steps = {
        1: (0, 0, 14000),
        2: (4000, 4000, 14000),
        3: (7700, 7700, 14000),
        4: (12100, 12100, 14000),
        5: (16200, 16200, 14000),
        6: (20300, 20300, 14000),
        7: (24400, 24400, 14000),
        8: (28500, 28500, 14000),
        9: (32000, 32000, 14000),
    }
    

    steps_motor_1, steps_motor_2, steps_motor_3 = gantry_steps.get(flavor_position, (0, 0, 0))
    PERMANENT_DIRECTION = {
    "horizontal_1": True,  # True for forward, False for reverse
    "horizontal_2": True,  # True for forward, False for reverse
    "gantry": False,        # True for forward, False for reverse
}

# Set the pin direction (input or output) for all motor pins
    ENABLE_PIN.direction = digitalio.Direction.OUTPUT
    for motor_name, motor in MOTOR_PINS.items():
        motor["direction"].value = PERMANENT_DIRECTION[motor_name] 
    if flavor_position == 9:
        move_stepper(MOTOR_PINS["gantry"], steps_motor_3, 'forward')
        move_stepper(MOTOR_PINS["horizontal_1"], steps_motor_1, 'forward')
        move_stepper(MOTOR_PINS["horizontal_2"], steps_motor_2, 'forward')
    else:
        max_steps = max(steps_motor_1, steps_motor_2, steps_motor_3)
        for step in range(max_steps):
            if step < steps_motor_1:
                MOTOR_PINS["horizontal_1"]["pulse"].value = True
            if step < steps_motor_2:
                MOTOR_PINS["horizontal_2"]["pulse"].value = True
            if step < steps_motor_3:
                MOTOR_PINS["gantry"]["pulse"].value = True

            time.sleep(0.00001)

            if step < steps_motor_1:
                MOTOR_PINS["horizontal_1"]["pulse"].value = False
            if step < steps_motor_2:
                MOTOR_PINS["horizontal_2"]["pulse"].value = False
            if step < steps_motor_3:
                MOTOR_PINS["gantry"]["pulse"].value = False

            time.sleep(0.00001)

def move_stepper1(motor_pins, steps, direction):
    GPIO.output(motor_pins['enable'], GPIO.LOW)  # Enable all motors
    GPIO.output(motor_pins['direction'], GPIO.HIGH if direction == 'forward' else GPIO.LOW)

    for _ in range(steps):
        GPIO.output(motor_pins['pulse'], GPIO.HIGH)
        time.sleep(0.00025)  # Pulse width
        GPIO.output(motor_pins['pulse'], GPIO.LOW)
        time.sleep(0.00025)

    GPIO.output(motor_pins['enable'], GPIO.HIGH)  # Disable all motors

# Function to dispense powder
def dispense_powder(flavor, qty):
    try:
        flavor_motor_pins = {
            1: {'enable': 4, 'pulse': 22, 'direction': 10},
            2: {'enable': 4, 'pulse': 9, 'direction': 11},
            3: {'enable': 4, 'pulse': 0, 'direction': 5},
            4: {'enable': 17, 'pulse': 6, 'direction': 13},
            5: {'enable': 17, 'pulse': 19, 'direction': 26},
            6: {'enable': 17, 'pulse': 14, 'direction': 15},
            7: {'enable': 27, 'pulse': 18, 'direction': 23},
            8: {'enable': 27, 'pulse': 24, 'direction': 25},
            9: {'enable': 27, 'pulse': 8, 'direction': 7},
        }

        if flavor not in flavor_motor_pins:
            raise ValueError("Invalid flavor selected, choose between 1 and 9.")

        motor_pins = flavor_motor_pins[flavor]

        GPIO.setup(motor_pins['enable'], GPIO.OUT)
        GPIO.setup(motor_pins['pulse'], GPIO.OUT)
        GPIO.setup(motor_pins['direction'], GPIO.OUT)

        GPIO.output(motor_pins['enable'], GPIO.LOW)
        print(f"Dispensing {qty} g  of flavor {flavor} ...") 

        if qty == 200:
            steps_per_revolution = 200
            stepper_rotations = 33
            powder_weight = 33
        elif qty == 400:
            steps_per_revolution = 200
            stepper_rotations = 100
            powder_weight = 100
         
        else:
            raise ValueError("Invalid quantity selected, must be 200ml or 400ml.")
        print(f"Dispensing {powder_weight} g  of flavor {flavor} ...")

        steps_to_dispense = steps_per_revolution * stepper_rotations

        move_stepper1(motor_pins, steps_to_dispense, 'forward')

        print(f"{powder_weight}g of Flavor {flavor} powder dispensed.")
        time.sleep(0.5)

    except Exception as e:
        print(f"Error dispensing powder: {e}")

# Main program
def main():
    try:
        GPIO.setmode(GPIO.BCM)

        flavor = int(input("Enter the flavor number (1-9): "))
        qty = int(input("Enter the quantity (200 or 400 ml): "))

        move_gantry_to_position(flavor)
        dispense_powder(flavor, qty)

    except Exception as e:
        print(f"Error in main program: {e}")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()