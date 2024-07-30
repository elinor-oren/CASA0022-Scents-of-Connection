import time
import math
import board
import neopixel

# NeoPixel setup
pixel_pin = board.D18
num_pixels = 60
ORDER = neopixel.GRBW
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.5, auto_write=False, pixel_order=ORDER)

# Define colors
teal = (0, 128, 128, 0)  # Turquoisey blue color

def breathing_effect(times, interval):
    steps = 200  # Increased number of steps for smoother breathing in and out
    hold_time = 1  # Hold time at peak brightness
    for _ in range(times):
        for step in range(steps):
            brightness = (math.sin(step / float(steps) * math.pi) + 1) / 2  
            for i in range(1, 22):
                pixels[i] = tuple(int(brightness * c) for c in teal)
            pixels.show()
            time.sleep(interval / steps)
        time.sleep(hold_time)  # Hold at peak brightness
        for step in range(steps):
            brightness = (math.sin((steps - step) / float(steps) * math.pi) + 1) / 2 
            for i in range(1, 22):
                pixels[i] = tuple(int(brightness * c) for c in teal)
            pixels.show()
            time.sleep(interval / steps)

try:
    while True:
        breathing_effect(1, 5)  # Run the breathing effect once, with 5 seconds interval for full cycle
except KeyboardInterrupt:
    pixels.fill((0, 0, 0, 0))
    pixels.show()
    print("Breathing effect test terminated.")
