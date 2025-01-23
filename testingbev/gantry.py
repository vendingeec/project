import time
import digitalio
from adafruit_mcp230xx.mcp23017 import MCP23017
import board
import busio

# Initialize I2C and MCP23017
i2c = busio.I2C(board.SCL, board.SDA)

# Check if I2C is working
if not i2c.try_lock():
    print("I2C bus is not available.")
    exit()

print("Initializing MCP23017 at address 0x24...")
mcp = MCP23017(i2c, address=0x24)

print("MCP23017 initialized successfully.")

# Define motor pins
pulse_pin = mcp.get_pin(0)
direction_pin = mcp.get_pin(1)
enable_pin = mcp.get_pin(6)

# Set pins as output
pulse_pin.direction = digitalio.Direction.OUTPUT
direction_pin.direction = digitalio.Direction.OUTPUT
enable_pin.direction = digitalio.Direction.OUTPUT

# Enable the motor
enable_pin.value = False  # Active low

# Set direction
direction_pin.value = True  # Forward

# Generate pulses
try:
    print("Rotating motor...")
    for _ in range(200):  # 2000 steps
        pulse_pin.value = True
        time.sleep(0.00001)  # Adjust for step timing
        pulse_pin.value = False
        time.sleep(0.00001)

    print("Rotation complete.")
    enable_pin.value = True  # Disable motor
except Exception as e:
    print(f"Error: {e}")
