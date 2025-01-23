import time
import RPi.GPIO as GPIO

# Setup GPIO for motors (stepper motor pin configuration)
def setup_motor_pins(motor_pins, enable_pin):
    # Setup the shared enable pin for all motors
    GPIO.setup(enable_pin, GPIO.OUT)
    GPIO.output(enable_pin, GPIO.HIGH)  # Default to disabled

    # Setup individual motor pins
    for motor, pins in motor_pins.items():
        GPIO.setup(pins['pulse'], GPIO.OUT)
        GPIO.setup(pins['direction'], GPIO.OUT)
        GPIO.output(pins['pulse'], GPIO.LOW)  # Default state
        GPIO.output(pins['direction'], GPIO.LOW)  # Default direction

# Stepper Motor Control Function (adjusted to use a shared enable pin)
def move_stepper(motor_pins, steps, direction, enable_pin):
    GPIO.output(enable_pin, GPIO.LOW)  # Enable all motors
    GPIO.output(motor_pins['direction'], GPIO.HIGH if direction == 'forward' else GPIO.LOW)

    for _ in range(steps):
        GPIO.output(motor_pins['pulse'], GPIO.HIGH)
        time.sleep(0.00025)  # Pulse width
        GPIO.output(motor_pins['pulse'], GPIO.LOW)
        time.sleep(0.00025)

    GPIO.output(enable_pin, GPIO.HIGH)  # Disable all motors

def move_gantry_to_position(rail_motor_pins, flavor_position, enable_pin):
    """
    Moves the gantry to the position corresponding to the selected flavor.

    Parameters:
    - rail_motor_pins: Dictionary containing 'pulse' and 'direction' pins for each motor.
    - flavor_position: The selected flavor position (1 to 9).
    - enable_pin: GPIO pin to enable/disable the motors.
    """
    # Predefined positions for each flavor (steps for gantry motors)
    gantry_steps = {
        1: (0, 0, 14000),  # Flavor 1 (example)
        2: (4000, 4000, 14000),  # Flavor 2 (example)
        3: (7700, 7700, 14000),  # Flavor 3 (example)
        4: (12100, 12100, 14000),  # Flavor 4 (example)
        5: (16200, 16200, 14000),  # Flavor 5 (example)
        6: (20300, 20300, 14000),  # Flavor 6 (example)
        7: (24400, 24400, 14000),  # Flavor 7 (example)
        8: (28500, 28500, 14000),  # Flavor 8 (example)
        9: (32000, 32000, 14000),  # Flavor 9 (example)
    }

    # Set permanent direction for each motor
    GPIO.output(rail_motor_pins['horizontal_1']['direction'], GPIO.HIGH)  # Fixed direction for horizontal motor 1
    GPIO.output(rail_motor_pins['horizontal_2']['direction'], GPIO.HIGH)  # Fixed direction for horizontal motor 2
    GPIO.output(rail_motor_pins['gantry']['direction'], GPIO.LOW)  # Fixed direction for gantry motor

    # Get the steps for the selected flavor position
    steps_motor_1, steps_motor_2, steps_motor_3 = gantry_steps.get(flavor_position, (0, 0, 0))

    # Ensure Enable Pin is active
    GPIO.output(enable_pin, GPIO.LOW)

    # If flavor 9 is selected, move the gantry motor first
    if flavor_position == 9:
        # Move the gantry motor first
        move_stepper(rail_motor_pins['gantry'], steps_motor_3, 'forward', enable_pin)

        # After gantry motor has moved, move the horizontal motors
        move_stepper(rail_motor_pins['horizontal_1'], steps_motor_1, 'forward', enable_pin)
        move_stepper(rail_motor_pins['horizontal_2'], steps_motor_2, 'forward', enable_pin)

    else:
        # For all other flavors, move all motors synchronously
        max_steps = max(steps_motor_1, steps_motor_2, steps_motor_3)

        # Move all motors synchronously
        for step in range(max_steps):
            # Pulse horizontal motor 1
            if step < steps_motor_1:
                GPIO.output(rail_motor_pins['horizontal_1']['pulse'], GPIO.HIGH)
            # Pulse horizontal motor 2
            if step < steps_motor_2:
                GPIO.output(rail_motor_pins['horizontal_2']['pulse'], GPIO.HIGH)
            # Pulse gantry motor
            if step < steps_motor_3:
                GPIO.output(rail_motor_pins['gantry']['pulse'], GPIO.HIGH)

            # Small delay for pulse
            time.sleep(0.00025)

            # Set pulse LOW for all motors
            GPIO.output(rail_motor_pins['horizontal_1']['pulse'], GPIO.LOW)
            GPIO.output(rail_motor_pins['horizontal_2']['pulse'], GPIO.LOW)
            GPIO.output(rail_motor_pins['gantry']['pulse'], GPIO.LOW)

            # Small delay between pulses
            time.sleep(0.00025)

    # Disable motors after movement
    GPIO.output(enable_pin, GPIO.HIGH)

# Powder Dispense Logic
def dispense_powder(flavor, qty, rail_motor_pins, enable_pin):
    try:
        # Define the pins for each of the 9 flavor stepper motors
        flavor_motor_pins = {
            1: {'enable': 17, 'pulse':19, 'direction': 26},  # Flavor 1 motor pins
            2: {'enable': 17, 'pulse': 14, 'direction': 15},  # Flavor 2 motor pins
            3: {'enable': 17, 'pulse': 18, 'direction': 23},  # Flavor 3 motor pins
            4: {'enable': 27, 'pulse': 24, 'direction': 25},    # Flavor 4 motor pins
            5: {'enable': 27, 'pulse': 8, 'direction': 7},   # Flavor 5 motor pins
            6: {'enable': 27, 'pulse': 1, 'direction': 12},    # Flavor 6 motor pins
            7: {'enable': 22, 'pulse': 16, 'direction': 20},   # Flavor 7 motor pins
            8: {'enable': 22, 'pulse': 21, 'direction': 27},    # Flavor 8 motor pins
            9: {'enable': 22, 'pulse': 8, 'direction': 0},     # Flavor 9 motor pins
        }

        # Check if the flavor is valid
        if flavor not in flavor_motor_pins:
            raise ValueError("Invalid flavor selected, choose between 1 and 9.")

        # Get the motor pins for the selected flavor
        motor_pins = flavor_motor_pins[flavor]

        # Setup the motor pins
        GPIO.setup(motor_pins['enable'], GPIO.OUT)
        GPIO.setup(motor_pins['pulse'], GPIO.OUT)
        GPIO.setup(motor_pins['direction'], GPIO.OUT)

        # Set the flavor motor to enabled
        GPIO.output(motor_pins['enable'], GPIO.LOW)

        # Powder dispensing logic based on quantity
        if qty == 200:  # Dispense 33g powder for 200ml
            steps_per_revolution = 200
            stepper_rotations = 20
            powder_weight = 33  # 33g for 200 ml
        elif qty == 400:  # Dispense 100g powder for 400ml
            steps_per_revolution = 200
            stepper_rotations = 100
            powder_weight = 100  # 100g for 400 ml
        else:
            raise ValueError("Invalid quantity selected, must be 200ml or 400ml.")

        # Calculate the total steps for the powder motor (flavor specific)
        steps_to_dispense = steps_per_revolution * stepper_rotations

        # Move the stepper motor to dispense powder
        move_stepper(motor_pins, steps_to_dispense, 'forward', enable_pin)


        # Print the powder dispensed message
        print(f"{powder_weight}g of Flavor {flavor} powder dispensed.")

        # Wait for 1 second before moving to the next station
        time.sleep(1)

    except Exception as e:
        print(f"Error dispensing powder: {e}")

# Main program
def main():
    try:
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)

        # Define the shared enable pin for all motors
        shared_enable_pin = 25  # Example shared enable pin for all motors

        # Define the motor pins for the gantry and flavor motors
        rail_motor_pins = {
            "horizontal_1": {"pulse": 23, "direction": 24},
    "horizontal_2": {"pulse": 26, "direction": 19},
    "gantry": {"pulse": 20, "direction": 21}
        }

        # Setup all motors
        setup_motor_pins(rail_motor_pins, shared_enable_pin)

        # Ask the user for flavor and quantity
        flavor = int(input("Enter the flavor number (1-9): "))
        qty = int(input("Enter the quantity (200 or 400 ml): "))

        # Example of moving gantry to a flavor position
        move_gantry_to_position(rail_motor_pins, flavor, shared_enable_pin)

        # Example of dispensing powder based on user input
        dispense_powder(flavor, qty, rail_motor_pins, shared_enable_pin)

    except Exception as e:
        print(f"Error in main program: {e}")
    finally:
        GPIO.cleanup()  # Clean up GPIO settings

if __name__ == "__main__":
    main()