import time
import board
import neopixel
import math
from threading import Lock

# NeoPixel setup
pixel_pin = board.D18
num_pixels = 60
ORDER = neopixel.GRBW
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=1.0, auto_write=False, pixel_order=ORDER)

# Define colors
color_levels = {
    1: (0, 0, 20, 0),   # very dark blue
    2: (0, 0, 60, 0),   # dark blue
    3: (0, 3, 90, 0),   # medium blue
    4: (0, 5, 120, 0),  # light blue
    5: (0, 8, 250, 0)   # white
}

white_color = (255, 255, 255, 0)  # Baseline white color

# Variables
lock = Lock()  # Lock to prevent interference between LEDs

def gradient_color(start_color, end_color, step, total_steps):
    """Interpolate between start_color and end_color."""
    return tuple(
        int(start_color[i] + (end_color[i] - start_color[i]) * (step / total_steps))
        for i in range(4)
    )

def gradient_effect(start_led, end_led, start_color, end_color, steps=50):
    for step in range(steps):
        color = gradient_color(start_color, end_color, step, steps - 1)
        for i in range(start_led, end_led + 1):
            if 0 <= i < num_pixels:  # Ensure we stay within range
                pixels[i] = color
        pixels.show()
        time.sleep(0.01)

def fixed_low_glow(start, end, color):
    for i in range(start, min(end + 1, num_pixels)):
        pixels[i] = color
    pixels.show()

def set_leds(meditation):
    with lock:
        # Determine the color based on meditation value
        level = analyze_meditation(meditation)
        start_color = color_levels[level]
        end_color = white_color  # Transition to white

        # Apply fade effect
        gradient_effect(22, 60, white_color, start_color, steps=100)

        if meditation <= 20:
            fixed_low_glow(22, 26, start_color)
            fixed_low_glow(57, 60, start_color)
        elif meditation <= 40:
            fixed_low_glow(22, 26, start_color)
            fixed_low_glow(57, 60, start_color)
            gradient_effect(27, 30, start_color, end_color)
            gradient_effect(56, 53, start_color, end_color)
        elif meditation <= 60:
            fixed_low_glow(22, 30, start_color)
            fixed_low_glow(53, 60, start_color)
            gradient_effect(31, 34, start_color, end_color)
            gradient_effect(52, 49, start_color, end_color)
        elif meditation <= 80:
            fixed_low_glow(22, 34, start_color)
            fixed_low_glow(49, 60, start_color)
            gradient_effect(35, 38, start_color, end_color)
            gradient_effect(48, 45, start_color, end_color)
        else:
            fixed_low_glow(22, 38, start_color)
            fixed_low_glow(45, 60, start_color)
            gradient_effect(39, 41, start_color, end_color)
            gradient_effect(44, 42, start_color, end_color)

def analyze_meditation(meditation):
    if meditation <= 25:
        return 1  # very low
    elif meditation <= 40:
        return 2  # slightly low
    elif meditation <= 60:
        return 3  # natural state
    elif meditation <= 80:
        return 4  # slightly high
    else:
        return 5  # very high

# Test function to display each meditation level for a few seconds
def test_led_levels():
    test_meditation_levels = [10, 30, 50, 70, 90]  # Example meditation levels
    for level in test_meditation_levels:
        print(f"Testing meditation level: {level}")
        set_leds(level)
        time.sleep(5)  # Display each level for 5 seconds

try:
    # Start with all LEDs in white
    pixels.fill(white_color)
    pixels.show()
    time.sleep(5)  # Display initial color for 5 seconds

    # Test each meditation level
    test_led_levels()
except KeyboardInterrupt:
    pixels.fill((0, 0, 0, 0))
    pixels.show()
    print("LED test terminated.")
