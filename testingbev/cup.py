import RPi.GPIO as GPIO
import time
import board
import busio
from adafruit_mcp230xx.mcp23017 import MCP23017
import digitalio

# I2C setup
i2c = busio.I2C(board.SCL, board.SDA)
mcp = MCP23017(i2c, address=0x24)

# GPIO Pins for Motor Control using MCP23017
PULSE_PIN = mcp.get_pin(7)    # Connect to the Pulse pin of DM542 (GPIO 2 on MCP23017)
DIR_PIN = mcp.get_pin(8)      # Connect to the Direction pin of DM542 (GPIO 3 on MCP23017)

# GPIO Pin for Enable Control (Raspberry Pi GPIO)
ENABLE_PIN = 10  # GPIO pin 17 for enabling cup dispensing motor

# Motor settings
STEPS_PER_REVOLUTION = 200  # Adjust based on your motor
CUP_DISPENSING_STEPS = 1200  # Steps required to dispense one cup
STEP_DELAY = 0.0005         # Delay between steps (adjust for speed)

def setup_motor():
    # Set up the MCP23017 pins as outputs
    PULSE_PIN.direction = digitalio.Direction.OUTPUT
    DIR_PIN.direction = digitalio.Direction.OUTPUT

    # Set the direction of the motor (HIGH or LOW)
    DIR_PIN.value = False  # LOW for one direction (or True for the opposite direction)

def setup_enable_pin():
    # Set up the Raspberry Pi GPIO pin for enabling the motor
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(ENABLE_PIN, GPIO.OUT)
    GPIO.output(ENABLE_PIN, GPIO.LOW)  # Default state (motor disabled)

def enable_motor():
    # Enable the motor by setting the enable pin HIGH
    GPIO.output(ENABLE_PIN, GPIO.HIGH)

def disable_motor():
    # Disable the motor by setting the enable pin LOW
    GPIO.output(ENABLE_PIN, GPIO.LOW)

def rotate_motor(steps, delay):
    for _ in range(steps):
        PULSE_PIN.value = True  # Set the pulse pin HIGH
        time.sleep(delay)
        PULSE_PIN.value = False  # Set the pulse pin LOW
        time.sleep(delay)

def dispense_cup():
    try:
        
        setup_enable_pin()# Enable the motor before starting the rotation
        enable_motor()

        setup_motor()
        rotate_motor(CUP_DISPENSING_STEPS, STEP_DELAY)
        print("Cup dispensed!")

        # Disable the motor after dispensing
        disable_motor()

    except KeyboardInterrupt:
        print("Program interrupted.")

if __name__ == "__main__":
    setup_enable_pin()  # Initialize the enable pin
    dispense_cup()
 
