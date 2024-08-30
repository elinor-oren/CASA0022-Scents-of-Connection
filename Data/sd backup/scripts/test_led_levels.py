import time
import board
import neopixel
import math

# NeoPixel setup
pixel_pin = board.D18
num_pixels = 60
ORDER = neopixel.GRBW
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.5, auto_write=False, pixel_order=ORDER)

# Define colors
yellowy_white = (255, 255, 100, 0)  # Yellowy white color
teal = (0, 128, 128, 0)  # Turquoisey blue color

def gentle_chaser(start_led, end_led, color, duration=1, interval=0.05):
    steps = int(duration / interval)
    for step in range(steps):
        brightness = (math.sin(step / float(steps) * math.pi * 2) + 1) / 2  # Value between 0 and 1
        for i in range(start_led, end_led + 1):
            if i < num_pixels:
                pixels[i] = tuple(int(brightness * c) for c in color)
        pixels.show()
        time.sleep(interval)

def fixed_low_glow(start_led, end_led, color):
    for i in range(start_led, end_led + 1):
        if i < num_pixels:
            pixels[i] = color
    pixels.show()

def set_leds(meditation):
    pixels.fill((0, 0, 0, 0))  # Clear all LEDs first
    pixels.show()
    
    if meditation <= 20:
        gentle_chaser(22, 25, teal)
        gentle_chaser(57, 60, teal)
    elif meditation <= 40:
        fixed_low_glow(22, 25, yellowy_white)
        fixed_low_glow(57, 60, yellowy_white)
        gentle_chaser(26, 29, teal)
        gentle_chaser(53, 56, teal)
    elif meditation <= 60:
        fixed_low_glow(22, 29, yellowy_white)
        fixed_low_glow(53, 60, yellowy_white)
        gentle_chaser(30, 33, teal)
        gentle_chaser(49, 52, teal)
    elif meditation <= 80:
        fixed_low_glow(22, 33, yellowy_white)
        fixed_low_glow(49, 60, yellowy_white)
        gentle_chaser(34, 37, teal)
        gentle_chaser(45, 48, teal)
    else:
        fixed_low_glow(22, 37, yellowy_white)
        fixed_low_glow(44, 60, yellowy_white)
        gentle_chaser(38, 40, teal)
        gentle_chaser(41, 44, teal)

def test_led_levels():
    meditation_levels = [20, 40, 60, 80, 90]
    for level in meditation_levels:
        print(f"Displaying LEDs for meditation level: {level}")
        set_leds(level)
        time.sleep(10)  # Display each level for 5 seconds

# Run the test
test_led_levels()
