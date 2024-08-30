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

# Define color levels with brightness scaling
color_levels = {
    1: (0, 0, 18, 0),   # very dark blue
    2: (0, 0, 39, 0),   # dark blue
    3: (0, 5, 80, 0),   # medium blue
    4: (0, 8, 150, 0),  # light blue
    5: (0, 10, 255, 0)  # white
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
        if start_led < end_led:
            index = start_led + step
        else:
            index = start_led - step
        if 0 <= index < num_pixels:  # Ensure we stay within range
            pixels[index] = color
    pixels.show()

def fixed_low_glow(start, end, color):
    for i in range(start, min(end + 1, num_pixels)):
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
        fixed_low_glow(22, 26, start_color)
        fixed_low_glow(57, 60, start_color)
#        gradient_effect(22, 26, start_color, end_color)
#        gradient_effect(60, 57, start_color, end_color)
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

# Test code to visualize the effect
try:
    while True:
        for meditation in range(0, 101, 10):
            print(f"Setting LEDs for meditation level {meditation}")
            set_leds(meditation)
            time.sleep(1)
except KeyboardInterrupt:
    pixels.fill((0, 0, 0, 0))
    pixels.show()
    print("Gradient effect test terminated.")
