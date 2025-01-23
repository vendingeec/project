import time
import board
import busio
import RPi.GPIO as GPIO
from adafruit_mcp230xx.mcp23017 import MCP23017
import digitalio

# Initialize I2C bus and MCP23017
i2c = busio.I2C(board.SCL, board.SDA)
mcp = MCP23017(i2c, address=0x24)

# Define MCP23017 pins for blender stepper (pulse and direction)
blender_pins = {
    'pulse': mcp.get_pin(4),  # Pin 4 for pulse
    'direction': mcp.get_pin(5)  # Pin 5 for direction
}

# Define MCP23017 pins for gear motor control
gear_motor_pins = {
    'IN1': mcp.get_pin(6),  # IN1 pin for L298N (direction control)
    'IN2': mcp.get_pin(7),  # IN2 pin for L298N (direction control)
    'ENA': mcp.get_pin(8)   # ENA pin for L298N (enable motor)
}

# Define GPIO pin for blender motor enable
blender_enable_pin = 10  # GPIO pin 17 for enabling blender motor

# Setup GPIO for blender motor enable pin
GPIO.setmode(GPIO.BCM)
GPIO.setup(blender_enable_pin, GPIO.OUT)
GPIO.output(blender_enable_pin, GPIO.LOW)  # Default state (motor disabled)

# Setup gear motor pins as outputs
gear_motor_pins['IN1'].direction = digitalio.Direction.OUTPUT
gear_motor_pins['IN2'].direction = digitalio.Direction.OUTPUT
gear_motor_pins['ENA'].direction = digitalio.Direction.OUTPUT

# Setup blender motor pins as outputs
blender_pins['pulse'].direction = digitalio.Direction.OUTPUT
blender_pins['direction'].direction = digitalio.Direction.OUTPUT

# Move gantry to position
def move_gantry_to_position_blender(rail_motor_pins, flavor_position, enable_pin):
    gantry_steps = {
        1: (37800, 37800, 7200),
        2: (33800, 33800, 7200),
        3: (29800, 29800, 7200),
        4: (25800, 25800, 7200),
        5: (21800, 21800, 7200),
        6: (17800, 17800, 7200),
        7: (13800, 13800, 7200),
        8: (9800, 9800, 7200),
        9: (5800, 5800, 7200),
    }

    steps_motor_1, steps_motor_2, steps_motor_3 = gantry_steps.get(flavor_position, (0, 0, 0))
    GPIO.output(enable_pin, GPIO.LOW)  # Enable motors

    # Define directions for each motor
    direction_motor_1 = 'forward' if steps_motor_1 > 0 else 'backward'
    direction_motor_2 = 'forward' if steps_motor_2 > 0 else 'backward'
    direction_motor_3 = 'forward' if steps_motor_3 > 0 else 'backward'

    # Set directions
    GPIO.output(rail_motor_pins['horizontal_1']['direction'], GPIO.HIGH if direction_motor_1 == 'forward' else GPIO.LOW)
    GPIO.output(rail_motor_pins['horizontal_2']['direction'], GPIO.HIGH if direction_motor_2 == 'forward' else GPIO.LOW)
    GPIO.output(rail_motor_pins['gantry']['direction'], GPIO.HIGH if direction_motor_3 == 'forward' else GPIO.LOW)

    if flavor_position == 9:
        # Move gantry motor first
        for step in range(steps_motor_3):
            GPIO.output(rail_motor_pins['gantry']['pulse'], GPIO.HIGH)
            time.sleep(0.00025)
            GPIO.output(rail_motor_pins['gantry']['pulse'], GPIO.LOW)
            time.sleep(0.00025)

        # Then move horizontal motors
        for step in range(max(steps_motor_1, steps_motor_2)):
            if step < steps_motor_1:
                GPIO.output(rail_motor_pins['horizontal_1']['pulse'], GPIO.HIGH)
            if step < steps_motor_2:
                GPIO.output(rail_motor_pins['horizontal_2']['pulse'], GPIO.HIGH)
            time.sleep(0.00025)
            GPIO.output(rail_motor_pins['horizontal_1']['pulse'], GPIO.LOW)
            GPIO.output(rail_motor_pins['horizontal_2']['pulse'], GPIO.LOW)
            time.sleep(0.00025)
    else:
        # Synchronous movement for flavors 1 to 8
        for step in range(max(steps_motor_1, steps_motor_2, steps_motor_3)):
            if step < steps_motor_1:
                GPIO.output(rail_motor_pins['horizontal_1']['pulse'], GPIO.HIGH)
            if step < steps_motor_2:
                GPIO.output(rail_motor_pins['horizontal_2']['pulse'], GPIO.HIGH)
            if step < steps_motor_3:
                GPIO.output(rail_motor_pins['gantry']['pulse'], GPIO.HIGH)
            time.sleep(0.00025)
            GPIO.output(rail_motor_pins['horizontal_1']['pulse'], GPIO.LOW)
            GPIO.output(rail_motor_pins['horizontal_2']['pulse'], GPIO.LOW)
            GPIO.output(rail_motor_pins['gantry']['pulse'], GPIO.LOW)
            time.sleep(0.00025)

    GPIO.output(enable_pin, GPIO.HIGH)  # Disable motors

# Move blender stepper
def move_blender_stepper(steps, step_delay_us, direction):
    blender_pins['direction'].value = direction  # Set direction for the motor
    for _ in range(steps):
        blender_pins['pulse'].value = True  # Send pulse
        time.sleep(step_delay_us / 1_000_000.0)
        blender_pins['pulse'].value = False  # Reset pulse
        time.sleep(step_delay_us / 1_000_000.0)

# Start gear motor
def start_gear_motor():
    gear_motor_pins['ENA'].value = True  # Enable motor
    gear_motor_pins['IN1'].value = True  # Set IN1 high for one direction
    gear_motor_pins['IN2'].value = False # Set IN2 low for one direction

# Stop gear motor
def stop_gear_motor():
    gear_motor_pins['ENA'].value = False  # Disable motor
    gear_motor_pins['IN1'].value = False # Set IN1 low to stop motor
    gear_motor_pins['IN2'].value = False # Set IN2 low to stop motor

# Reverse gear motor
def reverse_gear_motor():
    gear_motor_pins['ENA'].value = True  # Enable motor
    gear_motor_pins['IN1'].value = False # Set IN1 low to reverse direction
    gear_motor_pins['IN2'].value = True  # Set IN2 high to reverse direction

# Enable blender motor
def enable_blender_motor():
    GPIO.output(blender_enable_pin, GPIO.HIGH)  # Enable blender motor

# Disable blender motor
def disable_blender_motor():
    GPIO.output(blender_enable_pin, GPIO.LOW)  # Disable blender motor

# Blending sequence function
def blend(quantity_ml, rail_motor_pins, flavor_position, enable_pin):
    print(f"Starting blending process for {quantity_ml} ml...")

    # Move gantry to blender position
    move_gantry_to_position_blender(rail_motor_pins, flavor_position, enable_pin)

    # Enable the blender motor
    enable_blender_motor()

    # Move blender to blending position (downward)
    move_blender_stepper(steps=300, step_delay_us=200, direction=True)  # Adjust steps and delay as needed
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
        move_blender_stepper(steps=100, step_delay_us=2000, direction=True)
        time.sleep(0.1)
        # Small upward movement
        move_blender_stepper(steps=100, step_delay_us=2000, direction=False)
        time.sleep(0.1)

    # Stop the gear motor after blending
    stop_gear_motor()

    # Disable the blender motor
    disable_blender_motor()

    # Return blender to home position (upward)
    move_blender_stepper(steps=800, step_delay_us=50, direction=True)
    print("Blending completed. Returned to home position.")

# Washing sequence function
def washing(rail_motor_pins, flavor_position, enable_pin):
    print("Starting washing process...")
    
    # Move gantry to washing position
    move_gantry_to_position_blender(rail_motor_pins, flavor_position, enable_pin)
    
    time.sleep(2)  # 2-second delay before washing

    # Move to washing position
    move_blender_stepper(steps=900, step_delay_us=50, direction=False)
    time.sleep(0.5)

    # Run the gear motor for washing (5 seconds)
    start_gear_motor()
    time.sleep(5)
    stop_gear_motor()

    # Return to home position
    move_blender_stepper(steps=900, step_delay_us=50, direction=True)
    print("Washing completed. Returned to home position.")

# Main program
if __name__ == "__main__":
    try:
        flavor = int(input("Enter the flavor number (1-9): "))
        qty = int(input("Enter the quantity (200 or 400 ml): "))

        rail_motor_pins = {
            'horizontal_1': {'direction': 17, 'pulse': 18},
            'horizontal_2': {'direction': 22, 'pulse': 23},
            'gantry': {'direction': 24, 'pulse': 25}
        }

        enable_pin = 26  # Example enable pin for the motors

        blend(qty, rail_motor_pins, flavor, enable_pin)
        washing(rail_motor_pins, flavor, enable_pin)

    except KeyboardInterrupt:
        print("Program interrupted.")
    finally:
        GPIO.cleanup()
        print("GPIO cleaned up. Program exited.")
