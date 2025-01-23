from flask import Flask, request, jsonify
from flask_cors import CORS
import time
import RPi.GPIO as GPIO
from adafruit_mcp230xx.mcp23017 import MCP23017
import busio
import board
import digitalio

# Import the motor control functions
from cupback import dispense_cup
from waterback import dispense_water
from powderback import dispense_powder, move_gantry_to_position
from blenderback import blend, washing, move_gantry_to_position_blender
from proximity import check_proximity

# Flask app setup
app = Flask(__name__)
CORS(app)

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

# Set the pin direction (input or output) for all motor pins
ENABLE_PIN.direction = digitalio.Direction.OUTPUT
for motor in MOTOR_PINS.values():
    motor["pulse"].direction = digitalio.Direction.OUTPUT
    motor["direction"].direction = digitalio.Direction.OUTPUT

# Function to enable or disable motors
def enable_motors(enable=True):
    if enable:
        ENABLE_PIN.value = False  # Enable motors (LOW)
    else:
        ENABLE_PIN.value = True  # Disable motors (HIGH)

# Function to pulse the motor
def pulse_motor(motor_pins, steps, direction):
    enable_motors(True)  # Enable motors
    motor_pins["direction"].value = True if direction == 'forward' else False

    for step in range(steps):
        motor_pins["pulse"].value = True
        time.sleep(0.00001 )
        motor_pins["pulse"].value = False
        time.sleep(0.00001 )

    enable_motors(False)  # Disable motors

# Synchronous movement of horizontal motors
def move_horizontal_synchronously(motor_pins_1, motor_pins_2, steps, direction):
    enable_motors(True)  # Enable motors
    motor_pins_1["direction"].value = True if direction == 'forward' else False
    motor_pins_2["direction"].value = True if direction == 'forward' else False

    for step in range(steps):
        motor_pins_1["pulse"].value = True
        motor_pins_2["pulse"].value = True
        time.sleep(0.00001 )
        motor_pins_1["pulse"].value = False
        motor_pins_2["pulse"].value = False
        time.sleep(0.00001 )

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

        time.sleep(0.00001 )

        if step < steps_1:
            motor_pins_1["pulse"].value = False
        if step < steps_2:
            motor_pins_2["pulse"].value = False
        if step < steps_3:
            motor_pins_3["pulse"].value = False

        time.sleep(0.00001 )

    enable_motors(False)  # Disable motors

# Stepper motor control for individual motors
def move_stepper(motor_pins, steps, direction):
    enable_motors(True)  # Enable motors
    motor_pins["direction"].value = True if direction == 'forward' else False
    for step in range(steps):
        motor_pins["pulse"].value = True
        time.sleep(0.00001 )
        motor_pins["pulse"].value = False
        time.sleep(0.00001 )
    enable_motors(False)  # Disable motors

@app.route('/api/process-order', methods=['POST', 'OPTIONS'])
def process_order():
    if request.method == 'OPTIONS':
        return jsonify({"message": "CORS preflight passed"}), 200
    data = request.json
    print("Received request:", data)


    cup_type = data.get('cupType')
    flavor = int(data.get('flavor'))
    water_quantity = int(data.get('waterQuantity'))

    if flavor not in range(1, 10):
        return jsonify({'detail': 'Invalid flavor'}), 400
    if water_quantity not in [200, 400]:
        return jsonify({'detail': 'Invalid water quantity'}), 400

    try:
       

        # Step 1: Move to home position (Cup Dispensing Station)
        print("Step 1: At home position (Cup Dispensing Station)...")
        move_horizontal_synchronously(MOTOR_PINS["horizontal_1"], MOTOR_PINS["horizontal_2"], 0, "reverse")
        move_stepper(MOTOR_PINS["gantry"], 0, "reverse")
        time.sleep(0.5)

        if cup_type == "machine":
            # Step 2: Dispense cup at home position
            print("Step 2: Dispensing cup at home position...")
            dispense_cup()
        else:
            # Step 2: Move to delivery point to pick up user-provided cup
            print("Step 2: Moving to delivery point to pick up user-provided cup...")
            move_horizontal_synchronously(MOTOR_PINS["horizontal_1"], MOTOR_PINS["horizontal_2"], 35000, "forward")
            move_stepper(MOTOR_PINS["gantry"], 1500, "forward")
            print("Please place your cup in the designated area.")
            time.sleep(5)
            print("User cup detected ..")
              # Simulate waiting for user to place the cup

        # Step 3: Move to water dispensing station
        print("Step 3: Moving to water dispensing station...")
        if cup_type == "Machine Cup":
            # Move to the water dispensing station for machine cup
            move_stepper(MOTOR_PINS["gantry"], 6650, "reverse")
            move_horizontal_synchronously(MOTOR_PINS["horizontal_1"], MOTOR_PINS["horizontal_2"], 6900, "reverse")
        else:
            # Move to the water dispensing station for user-provided cup
            
            move_stepper(MOTOR_PINS["gantry"], 7000, "reverse")
            move_horizontal_synchronously(MOTOR_PINS["horizontal_1"], MOTOR_PINS["horizontal_2"], 7000, "reverse")

        dispense_water(water_quantity)

        # Step 4: Move to powder dispensing station
        print("Step 4: Moving to powder dispensing station...")
        move_gantry_to_position(flavor)  # Move gantry to correct position
        dispense_powder(flavor, water_quantity)

        # Step 5: Move to blender station
        print("Step 5: Moving to blender station...")
        move_gantry_to_position_blender(flavor)
        blend(water_quantity)

        # Step 6: Moving to delivery point (Three motors synchronously)
        print("Step 6: Moving to delivery point...")
        move_three_motors_synchronously(
            MOTOR_PINS["horizontal_1"], 
            MOTOR_PINS["horizontal_2"], 
            MOTOR_PINS["gantry"], 
            4200, 4200, 14700,  # Adjust steps for each motor
            "forward"
        )
        print("Please Take Your Drink")
        time.sleep(10)

        # Step 7: Returning to home position (Three motors synchronously)
        print("Step 7: Returning to home position (Cup Dispensing Station)...")
        move_three_motors_synchronously(
            MOTOR_PINS["horizontal_1"], 
            MOTOR_PINS["horizontal_2"], 
            MOTOR_PINS["gantry"], 
            35000, 35000, 5000,  # Adjust steps for each motor
            "reverse"
        )
        move_stepper(MOTOR_PINS["gantry"], 3600, "forward") 

        print("Process complete")
        return jsonify({'message': 'Order processed successfully'}), 200

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify({'detail': str(e)}), 500



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
    
