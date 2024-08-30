import time
import math
import board
import neopixel

# NeoPixel setup
pixel_pin = board.D18
num_pixels = 60
ORDER = neopixel.GRBW
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=1.0, auto_write=False, pixel_order=ORDER)

# Define warm yellow color
warm_yellow = (255, 150, 0, 0)  # Warm yellow color

def exaggerated_breathing_effect(times, interval):
    steps = 400  # Number of steps for breathing effect
    hold_time = 2  # Hold time at peak and minimum brightness
    min_brightness = 0.2  # Minimum brightness level
    max_brightness = 1.0  # Maximum brightness level

    for _ in range(times):
        # Breathe in
        for step in range(steps):
            brightness = min_brightness + (max_brightness - min_brightness) * (step / float(steps))
            color = tuple(int(brightness * c) for c in warm_yellow)
            for i in range(1, 21):
                pixels[i] = color
            pixels.show()
            time.sleep(interval / (2 * steps))

        time.sleep(hold_time)  # Hold at peak brightness

        # Breathe out
        for step in range(steps):
            brightness = max_brightness - (max_brightness - min_brightness) * (step / float(steps))
            color = tuple(int(brightness * c) for c in warm_yellow)
            for i in range(1, 22):
                pixels[i] = color
            pixels.show()
            time.sleep(interval / (1.5 * steps))  # Make breathe out more gradual

        time.sleep(hold_time)  # Hold at minimum brightness

try:
    while True:
        exaggerated_breathing_effect(1, 7)  # Adjust the interval as needed
except KeyboardInterrupt:
    pixels.fill((0, 0, 0, 0))
    pixels.show()
    print("Exaggerated breathing effect test terminated.")
