import time
import math
import board
import neopixel

# NeoPixel setup
pixel_pin = board.D18
num_pixels = 60
ORDER = neopixel.GRBW
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.1, auto_write=False, pixel_order=ORDER)

# Define colors
teal = (0, 128, 128, 0)  # Turquoisey blue color

def breathing_effect(times, interval):
    steps = 20  # Number of steps for breathing effect
    hold_time = 1.5  # Hold time at peak brightness
    min_brightness = 0.0  # Minimum brightness level
    max_brightness = 1.5  # Maximum brightness level
    
    for _ in range(times):
        # Breathe in
        for step in range(steps):
            brightness = min_brightness + (max_brightness - min_brightness) * (math.sin(step / float(steps) * math.pi) + 1) / 2
            pixels.brightness = brightness
            for i in range(1, 22):
                pixels[i] = teal
            pixels.show()
            time.sleep(interval / steps)
        time.sleep(hold_time)  # Hold at peak brightness

        # Breathe out
        for step in range(steps):
            brightness = min_brightness + (max_brightness - min_brightness) * (math.sin((steps - step) / float(steps) * math.pi) + 1) / 2
            pixels.brightness = brightness
            for i in range(1, 22):
                pixels[i] = teal
            pixels.show()
            time.sleep(interval / steps)

try:
    while True:
        breathing_effect(1, 5)  # Run the breathing effect once, with 5 seconds interval for full cycle
except KeyboardInterrupt:
    pixels.fill((0, 0, 0, 0))
    pixels.show()
    print("Breathing effect test terminated.")
