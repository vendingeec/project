import RPi.GPIO as GPIO
import time

# Define the GPIO pin for the water relay
WATER_RELAY_PIN = 18  # Example GPIO pin for water relay

# Function to setup GPIO for the water dispensing relay
def setup_water_relay():
    GPIO.setmode(GPIO.BCM)  # Set pin numbering mode to BCM
    GPIO.setup(WATER_RELAY_PIN, GPIO.OUT)
    GPIO.output(WATER_RELAY_PIN, GPIO.LOW)  # Default to off

# Function to dispense water based on quantity
def dispense_water(quantity):
    """
    Dispenses water based on the selected quantity.

    Parameters:
    quantity (int): Amount of water to dispense (200 or 400 ml).
    """
    try:
        # Setup GPIO for the relay
        setup_water_relay()

        # Determine the duration to run the pump
        if quantity == 200:
            duration = 7  # Relay on for 7 seconds for 200 ml
        elif quantity == 400:
            duration = 14  # Relay on for 14 seconds for 400 ml
        else:
            raise ValueError("Invalid water quantity. Choose either 200 ml or 400 ml.")

        # Activate the relay (turn on the water pump)
        print(f"Dispensing {quantity} ml of water...")  # Step 3 in main program
        GPIO.output(WATER_RELAY_PIN, GPIO.HIGH)
        time.sleep(duration)  # Wait for the required time (to dispense water)
        GPIO.output(WATER_RELAY_PIN, GPIO.LOW)  # Turn off the relay (stop the pump)
        print(f"Successfully dispensed {quantity} ml of water.")

    except Exception as e:
        print(f"Error dispensing water: {e}")

# Main block to run the program
if __name__ == "__main__":
    # Ask user for the quantity of water to dispense
    try:
        quantity = int(input("Enter quantity (200 or 400 ml): "))
        dispense_water(quantity)
    except ValueError:
        print("Invalid input. Please enter 200 or 400.")
