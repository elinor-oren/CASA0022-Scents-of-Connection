import board
import neopixel
import time

# Configuration for the NeoPixel strip
LED_COUNT = 60  # Total number of LEDs in the strip
LED_PIN = board.D18  # GPIO pin connected to the NeoPixels (must support PWM!)
LED_BRIGHTNESS = 0.4  # Set brightness (0.0 to 1.0, where 1.0 is the brightest)

# List of possible LED orders
orders = [neopixel.RGBW, neopixel.GRBW, neopixel.RBGW, neopixel.GBRW, neopixel.BRGW]

def light_strip(order):
    # Create a NeoPixel object
    strip = neopixel.NeoPixel(LED_PIN, LED_COUNT, brightness=LED_BRIGHTNESS, auto_write=False, pixel_order=order)
    
    # Set the first half of the strip to yellowy white
    for i in range(LED_COUNT // 2):
        strip[i] = (255, 255, 200, 50)  # Yellowy white

    # Set the second half of the strip to scarlet burnt orange
    for i in range(LED_COUNT // 2, LED_COUNT):
        strip[i] = (255, 80, 0, 0)  # Scarlet burnt orange

    # Update the strip to show the new colors
    strip.show()

# Test each order to see which one matches the physical configuration of your strip
for order in orders:
    light_strip(order)
    print(f"Testing color order: {order}")
    time.sleep(10)  # Keep each test running for 10 seconds

# Optionally, turn off all LEDs after the test
strip.fill((0, 0, 0, 0))
strip.show()
