import time
import math
import board
import neopixel
from threading import Lock  # Import the Lock class

# NeoPixel setup
pixel_pin = board.D18
num_pixels = 60
ORDER = neopixel.GRBW
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=1.0, auto_write=False, pixel_order=ORDER)

# Define color levels
color_levels = {
    1: (0, 0, 128, 0),   # dark blue
    2: (0, 0, 255, 0),   # medium blue
    3: (0, 128, 255, 0), # light blue with same tone
    4: (0, 200, 255, 0), # brighter blue with same tone
    5: (255, 255, 255, 0)  # white
}

lock = Lock()
rainbow_running = False

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

def gradient_color(start_color, end_color, step, total_steps):
    """Interpolate between start_color and end_color."""
    return tuple(
        int(start_color[i] + (end_color[i] - start_color[i]) * (step / total_steps))
        for i in range(4)
    )

def gradient_effect(start_led, end_led, start_color, end_color):
    total_steps = abs(end_led - start_led) + 1
    for step in range(total_steps):
        color = gradient_color(start_color, end_color, step, total_steps - 1)
        index = start_led + step if start_led < end_led else start_led - step
        if index < num_pixels:  # Ensure we stay within range
            pixels[index] = color
    pixels.show()

def fixed_low_glow(start, end, color):
    for i in range(start, min(end, num_pixels)):
        pixels[i] = color
    pixels.show()

def set_leds(meditation):
    with lock:
        if rainbow_running:
            return
        pixels.fill((0, 0, 0, 0))  # Clear all LEDs first
        pixels.show()

    # Determine the color based on meditation value
    level = analyze_meditation(meditation)
    start_color = color_levels[level]
    end_color = (255, 255, 255, 0)  # Transition to white

    if meditation <= 20:
        gradient_effect(26, 22, start_color, end_color)  # Reversed direction
        gradient_effect(60, 57, start_color, end_color)  # Reversed direction
    elif meditation <= 40:
        fixed_low_glow(22, 26, start_color)
        fixed_low_glow(57, 60, start_color)
        gradient_effect(30, 27, start_color, end_color)  # Reversed direction
        gradient_effect(56, 53, start_color, end_color)  # Reversed direction
    elif meditation <= 60:
        fixed_low_glow(22, 30, start_color)
        fixed_low_glow(53, 60, start_color)
        gradient_effect(34, 31, start_color, end_color)  # Reversed direction
        gradient_effect(52, 49, start_color, end_color)  # Reversed direction
    elif meditation <= 80:
        fixed_low_glow(22, 34, start_color)
        fixed_low_glow(49, 60, start_color)
        gradient_effect(38, 35, start_color, end_color)  # Reversed direction
        gradient_effect(48, 45, start_color, end_color)  # Reversed direction
    else:
        fixed_low_glow(22, 38, start_color)
        fixed_low_glow(45, 60, start_color)
        gradient_effect(41, 39, start_color, end_color)  # Reversed direction
        gradient_effect(44, 42, start_color, end_color)  # Reversed direction

# Test the set_leds function
try:
    while True:
        for meditation in range(0, 101, 20):  # Test with meditation values from 0 to 100
            print(f"Setting LEDs for meditation level {meditation}")
            set_leds(meditation)
            time.sleep(2)  # Wait 2 seconds between each level to observe the effect
except KeyboardInterrupt:
    pixels.fill((0, 0, 0, 0))
    pixels.show()
    print("Test terminated.")
