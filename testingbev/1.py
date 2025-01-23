from flask import Flask, request, jsonify
from cup import dispense_cup
from water import dispense_water
from powder import dispense_powder, move_gantry_to_position
from blender import blend, washing, move_gantry_to_position_blender
from proximity import check_proximity
import time
from adafruit_mcp230xx.mcp23017 import MCP23017
import board
import busio
import digitalio
from flask_cors import CORS

print("Initializing MCP23017 I/O expander...")
i2c = busio.I2C(board.SCL, board.SDA)
mcp = MCP23017(i2c, address=0x24)  # MCP23017 at address 0x24
print("MCP23017 initialized.")

# Flask app setup
app = Flask(__name__)
CORS(app)

motor_pins = {
    "horizontal_1": {"pulse": mcp.get_pin(0), "direction": mcp.get_pin(1)},
    "horizontal_2": {"pulse": mcp.get_pin(2), "direction": mcp.get_pin(3)},
    "gantry": {"pulse": mcp.get_pin(4), "direction": mcp.get_pin(5)}
}



ENABLE_PIN = 6  # Shared Enable Pin for all motors
# Set up MCP23017 pins as outputs
for motor_name, motor_pins in motor_pins.items():
    # Set the pulse and direction pins as outputs
    motor_pins["pulse"].direction = digitalio.Direction.OUTPUT
    motor_pins["direction"].direction = digitalio.Direction.OUTPUT

# Enable Pin Setup
enable_pin = mcp.get_pin(ENABLE_PIN)
enable_pin.direction = digitalio.Direction.OUTPUT


# Synchronous movement of horizontal motors
def move_horizontal_synchronously(motor_pins_1, motor_pins_2, steps, direction):
    enable_pin.value = False  # Enable all motors
    motor_pins_1['direction'].value = True if direction == 'forward' else False
    motor_pins_2['direction'].value = True if direction == 'forward' else False

    for step in range(steps):
        motor_pins_1['pulse'].value = True
        motor_pins_2['pulse'].value = True
        time.sleep(0.00025)
        motor_pins_1['pulse'].value = False
        motor_pins_2['pulse'].value = False
        time.sleep(0.00025)

    enable_pin.value = True  # Disable all motors
def move_stepper(motor_pins, steps, direction):
    # Set the direction pin
    motor_pins['direction'].value = True if direction == 'forward' else False

    # Enable the motor (set ENABLE_PIN as output and active low)
    ENABLE_PIN.value = False  # Assuming ENABLE_PIN is set up as a digital output pin

    # Pulse the motor for the given number of steps
    for step in range(steps):
        motor_pins['pulse'].value = True
        time.sleep(0.00025)  # Adjust pulse width as needed
        motor_pins['pulse'].value = False
        time.sleep(0.00025)

    # Disable the motor after movement
    ENABLE_PIN.value = True  # Disable the motor (active high)

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

        time.sleep(0.00025)

        if step < steps_1:
            motor_pins_1['pulse'].value = False
        if step < steps_2:
            motor_pins_2['pulse'].value = False
        if step < steps_3:
            motor_pins_3['pulse'].value = False

        time.sleep(0.00025)

    enable_pin.value = True  # Disable all motors

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
        # Step 1: Home Position
        print("Step 1: Moving to home position...")
        print(f"Direction pin: {motor_pins['direction']}")
        print(f"Pulse pin: {motor_pins['pulse']}")


        move_horizontal_synchronously(motor_pins["horizontal_1"], motor_pins["horizontal_2"], 0, "reverse")
        move_stepper(motor_pins["gantry"], 0, "reverse")
        time.sleep(0.5)
        print("At home position.")

        # Step 2: Dispense or Move to User Cup
        if cup_type == "machine":
            print("Step 2: Dispensing cup from machine...")
            dispense_cup()
            print("Cup dispensed.")
        else:
            print("Step 2: Moving to user-provided cup position...")
            move_horizontal_synchronously(motor_pins["horizontal_1"], motor_pins["horizontal_2"], 35000, "forward")
            move_stepper(motor_pins["gantry"], 1500, "forward")
            time.sleep(5)
            print("Positioned at user-provided cup.")

        # Step 3: Water Dispensing
        print("Step 3: Moving to water dispensing position...")
        if cup_type == "machine":
            move_stepper(motor_pins["gantry"], 6650, "reverse")
            move_horizontal_synchronously(motor_pins["horizontal_1"], motor_pins["horizontal_2"], 6900, "reverse")
        else:
            move_stepper(motor_pins["gantry"], 7000, "reverse")
            move_horizontal_synchronously(motor_pins["horizontal_1"], motor_pins["horizontal_2"], 7000, "reverse")
        print("At water dispensing position.")
        dispense_water(water_quantity)
        print("Water dispensed.")

        # Step 4: Powder Dispensing
        print("Step 4: Moving to powder dispensing position...")
        print(f"Dispensing powder for flavor {flavor}...")
        dispense_powder(flavor, water_quantity, motor_pins, ENABLE_PIN)
        print("Powder dispensed.")

        # Step 5: Blender
        print("Step 5: Moving to blender position...")
        print("Blending contents...")
        blend(water_quantity, motor_pins, flavor, ENABLE_PIN)
        print("Blending completed.")

        # Step 6: Delivery
        print("Step 6: Moving to delivery position...")
        move_three_motors_synchronously(
            motor_pins["horizontal_1"], 
            motor_pins["horizontal_2"], 
            motor_pins["gantry"], 
            4200, 4200, 14700, "forward")
        time.sleep(10)
        print("Delivery completed.")

        # Step 7: Return to Home
        print("Step 7: Returning to home position...")
        move_three_motors_synchronously(    
            motor_pins["horizontal_1"], 
            motor_pins["horizontal_2"], 
            motor_pins["gantry"], 
            35000, 35000, 5000, "reverse")
        move_stepper(motor_pins["gantry"], 3600, "forward")
        print("Returned to home position.")

        return jsonify({'message': 'Order processed successfully'}), 200

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify({'detail': str(e)}), 500



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
