import RPi.GPIO as GPIO
import time

# Set up GPIO mode
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Define the pin for the proximity sensor
PROXIMITY_PIN = 17  # Change this to the GPIO pin you're using

# Set up the proximity sensor pin as input
GPIO.setup(PROXIMITY_PIN, GPIO.IN)

def check_proximity():
    try:
        while True:
            # Read the state of the proximity sensor
            sensor_state = GPIO.input(PROXIMITY_PIN)

            if sensor_state == GPIO.HIGH:
                print("Object detected!")
            else:
                print("No object detected.")

            # Wait for a short period before checking again
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("Program interrupted. Cleaning up...")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    check_proximity()
