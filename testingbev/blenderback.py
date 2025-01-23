import time
import RPi.GPIO as GPIO
from adafruit_mcp230xx.mcp23017 import MCP23017
import busio
import board
import digitalio

GPIO.setmode(GPIO.BCM)

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
    motor["direction"].value = PERMANENT_DIRECTION[motor_name] 

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

# Movimport time

def move_gantry_to_position_blender( flavor_position):
    gantry_steps = {
        1: (37800, 37800, 7600),
        2: (33800, 33800, 7600),
        3: (29800, 29800, 7600),
        4: (25800, 25800, 7600),
        5: (21800, 21800, 7600),
        6: (17800, 17800, 7600),
        7: (13800, 13800, 7600),
        8: (9800, 9800, 7600),
        9: (5800, 5800, 7600),
    }

    steps_motor_1, steps_motor_2, steps_motor_3 = gantry_steps.get(flavor_position, (0, 0, 0))

    # Enable motors
    ENABLE_PIN.value = False

    # Define directions for each motor
    direction_motor_1 = steps_motor_1 > 0
    direction_motor_2 = steps_motor_2 > 0
    direction_motor_3 = steps_motor_3 > 0

    # Set directions
    MOTOR_PINS['horizontal_1']['direction'].value = direction_motor_1
    MOTOR_PINS['horizontal_2']['direction'].value = direction_motor_2
    MOTOR_PINS['gantry']['direction'].value = direction_motor_3


    if flavor_position == 9:
        # Move gantry motor first
        for step in range(abs(steps_motor_3)):
            MOTOR_PINS['gantry']['pulse'].value = True
            time.sleep(0.00025)
            MOTOR_PINS['gantry']['pulse'].value = False
            time.sleep(0.00025)

        # Then move horizontal motors
        for step in range(max(abs(steps_motor_1), abs(steps_motor_2))):
            if step < abs(steps_motor_1):
                MOTOR_PINS['horizontal_1']['pulse'].value = True
            if step < abs(steps_motor_2):
                MOTOR_PINS['horizontal_2']['pulse'].value = True
            time.sleep(0.00001)
            MOTOR_PINS['horizontal_1']['pulse'].value = False
            MOTOR_PINS['horizontal_2']['pulse'].value = False
            time.sleep(0.00001)
    else:
        # Synchronous movement for flavors 1 to 8
        for step in range(max(abs(steps_motor_1), abs(steps_motor_2), abs(steps_motor_3))):
            if step < abs(steps_motor_1):
                MOTOR_PINS['horizontal_1']['pulse'].value = True
            if step < abs(steps_motor_2):
                MOTOR_PINS['horizontal_2']['pulse'].value = True
            if step < abs(steps_motor_3):
                MOTOR_PINS['gantry']['pulse'].value = True
            time.sleep(0.00001)
            MOTOR_PINS['horizontal_1']['pulse'].value = False
            MOTOR_PINS['horizontal_2']['pulse'].value = False
            MOTOR_PINS['gantry']['pulse'].value = False
            time.sleep(0.00001)

    # Disable motors
    ENABLE_PIN.value = True


blender_pins = {
    'pulse': 18,  # Replace with your actual GPIO pin number
    'direction': 23,  # Replace with your actual GPIO pin number
    'enable': 24  # Enable pin for blender stepper motor
}

gear_motor_pins = {
    'IN1': 10,  # Replace with your actual GPIO pin number
    'IN2': 9    # Replace with your actual GPIO pin number
}

# Setup GPIO for blender stepper motor
GPIO.setup(blender_pins['pulse'], GPIO.OUT)
GPIO.setup(blender_pins['direction'], GPIO.OUT)
GPIO.setup(blender_pins['enable'], GPIO.OUT)
GPIO.output(blender_pins['pulse'], GPIO.LOW)
GPIO.output(blender_pins['direction'], GPIO.LOW)
GPIO.output(blender_pins['enable'], GPIO.LOW)  # Default to disabled

# Setup GPIO for gear motor
GPIO.setup(gear_motor_pins['IN1'], GPIO.OUT)
GPIO.setup(gear_motor_pins['IN2'], GPIO.OUT)
GPIO.output(gear_motor_pins['IN1'], GPIO.LOW)
GPIO.output(gear_motor_pins['IN2'], GPIO.LOW)

# Stepper Motor Control Function
def move_blender_stepper(steps, step_delay_us, direction):
    GPIO.output(blender_pins['enable'], GPIO.HIGH)  # Enable the blender stepper motor
    GPIO.output(blender_pins['direction'], direction)
    for _ in range(steps):
        GPIO.output(blender_pins['pulse'], GPIO.HIGH)
        time.sleep(step_delay_us / 1_000_000.0)
        GPIO.output(blender_pins['pulse'], GPIO.LOW)
        time.sleep(step_delay_us / 1_000_000.0)
    GPIO.output(blender_pins['enable'], GPIO.LOW)  # Disable the blender stepper motor

# Start gear motor
def start_gear_motor():
    GPIO.output(gear_motor_pins['IN1'], GPIO.HIGH)
    GPIO.output(gear_motor_pins['IN2'], GPIO.LOW)

# Stop gear motor
def stop_gear_motor():
    GPIO.output(gear_motor_pins['IN1'], GPIO.LOW)
    GPIO.output(gear_motor_pins['IN2'], GPIO.LOW)

# Blending sequence function
def blend(quantity_ml):
    print(f"Starting blending process for {quantity_ml} ml...")

    # Move blender to blending position (downward)
    move_blender_stepper(steps=300, step_delay_us=200, direction=GPIO.HIGH)  # Adjust steps and delay as needed
    time.sleep(0.3)  # Small delay after moving down

    # Start gear motor for blending
    start_gear_motor()

    # Set blend duration based on quantity
    if quantity_ml == 200:
        blend_duration = 5  # Blend for 5 seconds for 200 ml
    elif quantity_ml == 400:
        blend_duration = 8  # Blend for 8 seconds for 400 ml
    else:
        print("Invalid quantity. Please choose 200 ml or 400 ml.")
        return

    # Oscillate up and down while blending
    start_time = time.time()
    while time.time() - start_time < blend_duration:
        # Small downward movement
        move_blender_stepper(steps=100, step_delay_us=2000, direction=GPIO.HIGH)
        time.sleep(0.1)
        # Small upward movement
        move_blender_stepper(steps=100, step_delay_us=2000, direction=GPIO.LOW)
        time.sleep(0.1)

    # Stop the gear motor after blending
    stop_gear_motor()

    # Return blender to home position (upward)
    move_blender_stepper(steps=800, step_delay_us=50, direction=GPIO.HIGH)
    print("Blending completed. Blender Returned to home position.")
    time.sleep(0.5) 
# Washing sequence function
def washing():
    print("Starting washing process...")
    time.sleep(2)  # 2-second delay before washing

    # Move to washing position
    move_blender_stepper(steps=900, step_delay_us=50, direction=GPIO.LOW)
    time.sleep(0.5)

    # Run the gear motor for washing (5 seconds)
    start_gear_motor()
    time.sleep(5)
    stop_gear_motor()

    # Return to home position
    move_blender_stepper(steps=900, step_delay_us=50, direction=GPIO.HIGH)
    print("Washing completed. Returned to home position.")
# Main program
if __name__ == "__main__":
    try:
# Default state

        flavor = int(input("Enter the flavor number (1-9): "))
        qty = int(input("Enter the quantity (200 or 400 ml): "))

        move_gantry_to_position_blender(flavor)
        blend(qty)
        washing()

    except KeyboardInterrupt:
        print("Program interrupted.")
    finally:
        GPIO.cleanup()
        print("GPIO cleaned up. Program exited.")
