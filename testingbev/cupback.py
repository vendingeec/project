import RPi.GPIO as GPIO
import time

# GPIO Pins
PULSE_PIN = 14    # Connect to the Pulse pin of DM542
DIR_PIN = 15     # Connect to the Direction pin of DM542

# Motor settings
STEPS_PER_REVOLUTION = 200  # Adjust based on your motor
CUP_DISPENSING_STEPS = 1200  # Steps required to dispense one cup
STEP_DELAY = 0.0005         # Delay between steps (adjust for speed)

def setup_motor():
    GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering
    GPIO.setup(PULSE_PIN, GPIO.OUT)
    GPIO.setup(DIR_PIN, GPIO.OUT)
    GPIO.output(DIR_PIN, GPIO.LOW)  # Set direction (HIGH or LOW)

def rotate_motor(steps, delay):
    for _ in range(steps):
        GPIO.output(PULSE_PIN, GPIO.HIGH)
        time.sleep(delay)
        GPIO.output(PULSE_PIN, GPIO.LOW)
        time.sleep(delay)
        

def dispense_cup():
    try:
        setup_motor()
        rotate_motor(CUP_DISPENSING_STEPS, STEP_DELAY)
        print("Cup dispensed!")
    except KeyboardInterrupt:
        print("Program interrupted.")
 

if __name__ == "__main__":
    dispense_cup()