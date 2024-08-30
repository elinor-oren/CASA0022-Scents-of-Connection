import time
import math
import board
import neopixel
from threading import Lock

# NeoPixel setup
pixel_pin = board.D18
num_pixels = 60
ORDER = neopixel.GRBW
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=1.0, auto_write=False, pixel_order=ORDER)

# Define colors
yellowy_white = (255, 255, 100, 0)  # Yellowy white color
tangerine = (255, 80, 0, 0)  # Tangerine orange color
teal = (0, 128, 128, 0)  # Turquoisey blue color

color_levels = {
    1: (0, 0, 128, 0),   # dark blue
    2: (0, 0, 255, 0),   # medium blue
    3: (0, 128, 255, 0), # light blue
    4: (128, 255, 255, 0), # pale blue
    5: (255, 255, 255, 0)  # white
}

# Lock to prevent interference between LEDs
lock = Lock()

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
        if 0 <= index < num_pixels:  # Ensure we stay within range
            pixels[index] = color
    pixels.show()

def fixed_low_glow(start, end, color):
    for i in range(start, min(end + 1, num_pixels)):
        pixels[i] = color
    pixels.show()

def set_leds(meditation, progress=1.0):
    with lock:
        pixels.fill((0, 0, 0, 0))  # Clear all LEDs first
        pixels.show()

        # Determine the color based on meditation value
        level = analyze_meditation(meditation)
        start_color = color_levels[level]
        end_color = (255, 255, 255, 0)  # Transition to white

        if level == 1:
            gradient_effect(22, 26, start_color, end_color)
            gradient_effect(57, 60, start_color, end_color)
        elif level == 2:
            fixed_low_glow(22, 26, start_color)
            fixed_low_glow(57, 60, start_color)
            gradient_effect(27, 30, start_color, end_color)
            gradient_effect(56, 53, start_color, end_color)
        elif level == 3:
            fixed_low_glow(22, 30, start_color)
            fixed_low_glow(53, 60, start_color)
            gradient_effect(31, 34, start_color, end_color)
            gradient_effect(52, 49, start_color, end_color)
        elif level == 4:
            fixed_low_glow(22, 34, start_color)
            fixed_low_glow(49, 60, start_color)
            gradient_effect(35, 38, start_color, end_color)
            gradient_effect(48, 45, start_color, end_color)
        elif level == 5:
            fixed_low_glow(22, 38, start_color)
            fixed_low_glow(45, 60, start_color)
            gradient_effect(39, 41, start_color, end_color)
            gradient_effect(44, 42, start_color, end_color)

def smooth_transition(target_function, *args, duration=0.5, interval=0.05):
    steps = int(duration / interval)
    for step in range(steps):
        target_function(*args, step / float(steps))
        pixels.show()
        time.sleep(interval)

def analyze_meditation(meditation):
    if meditation <= 20:
        return 1  # very low
    elif meditation <= 40:
        return 2  # slightly low
    elif meditation <= 60:
        return 3  # natural state
    elif meditation <= 80:
        return 4  # slightly high
    else:
        return 5  # very high

def test_smooth_transition():
    levels = [10, 30, 50, 70, 90]
    for level in levels:
        print(f"Setting LEDs for meditation level {level}")
        smooth_transition(set_leds, level, duration=1.0, interval=0.05)
        time.sleep(1)

# Run the test
try:
    test_smooth_transition()
except KeyboardInterrupt:
    pixels.fill((0, 0, 0, 0))
    pixels.show()
    print("Test terminated.")
