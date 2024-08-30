import RPi.GPIO as GPIO
import time

# Use BCM GPIO numbering
GPIO.setmode(GPIO.BCM)

# Set GPIO17 as an output pin
GPIO.setup(17, GPIO.OUT)

try:
    while True:
        # Turn GPIO17 on
        GPIO.output(17, GPIO.HIGH)
        print("GPIO17 is ON")
        time.sleep(8)  # Wait for 1 second

        # Turn GPIO17 off
        GPIO.output(17, GPIO.LOW)
        print("GPIO17 is OFF")
        time.sleep(5)  # Wait for 1 second

except KeyboardInterrupt:
    # Clean up GPIO settings before exiting
    GPIO.cleanup()
    print("Exiting and cleaning up GPIO settings")

