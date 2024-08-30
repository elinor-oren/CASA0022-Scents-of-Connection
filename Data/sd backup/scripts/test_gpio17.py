import RPi.GPIO as GPIO
import time

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)

try:
    # Turn on GPIO 17
    GPIO.output(17, GPIO.HIGH)
    print("GPIO 17 set to HIGH. Waiting for 10 seconds...")
    time.sleep(10)  # Wait for 10 seconds

    # Turn off GPIO 17
    GPIO.output(17, GPIO.LOW)
    print("GPIO 17 set to LOW.")

finally:
    # Clean up GPIO settings
    GPIO.cleanup()
