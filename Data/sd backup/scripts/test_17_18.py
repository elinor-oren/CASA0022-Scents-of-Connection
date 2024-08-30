import RPi.GPIO as GPIO
import time

# Set the GPIO mode
GPIO.setmode(GPIO.BCM)

# Define the pin number
control_pin = 17  # Change to 18 to test GPIO 18

# Setup the GPIO pin as output
GPIO.setup(control_pin, GPIO.OUT)

try:
    # Turn on the pin
    GPIO.output(control_pin, GPIO.HIGH)
    print(f"GPIO {control_pin} set to HIGH. Waiting for 5 seconds...")
    time.sleep(5)  # Wait for 5 seconds

    # Turn off the pin
    GPIO.output(control_pin, GPIO.LOW)
    print(f"GPIO {control_pin} set to LOW.")

finally:
    # Clean up GPIO settings
    GPIO.cleanup()
