import board
import neopixel
import time

# Configuration for the NeoPixel strip
LED_COUNT = 60  # Total number of LEDs in the strip
LED_PIN = board.D18  # GPIO pin connected to the NeoPixels (must support PWM!)
LED_BRIGHTNESS = 0.4  # Set brightness (0.0 to 1.0, where 1.0 is the brightest)
LED_ORDER = neopixel.GRBW  # Order of the color channels, adjust if necessary

# Create a NeoPixel object
strip = neopixel.NeoPixel(LED_PIN, LED_COUNT, brightness=LED_BRIGHTNESS, auto_write=False, pixel_order=LED_ORDER)

def light_half_strip():
    # Calculate the midpoint of the strip
    mid_point = (LED_COUNT + 24) // 2

    # Set the first half of the strip to green
    for i in range(mid_point):
        strip[i] = (0, 255, 0,0)  # Green color

    # Set the second half of the strip to blue
    for i in range(mid_point, LED_COUNT):
        strip[i] = (0, 0, 255,0)  # Blue color

    # Update the strip to show the new colors
    strip.show()

# Run the function to light up the strip
light_half_strip()

# Keep the program running for 10 seconds to display the colors
time.sleep(10)

# Optionally, turn off all LEDs after the test
strip.fill((0, 0, 0, 0))
strip.show()
