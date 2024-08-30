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
yellowy_white = (255, 255, 100, 0)  # Yellowy white color
teal = (0, 128, 128, 0)  # Turquoisey blue color
warm_yellow = (255, 150, 0, 0)  # Warm yellow color

# Variables
lock = Lock()  # Lock to prevent interference between LEDs
current_colors = [(0, 0, 0, 0)] * num_pixels

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

def smooth_transition(target_colors, steps=50):
    global current_colors
    for step in range(steps):
        for i in range(num_pixels):
            current_colors[i] = gradient_color(current_colors[i], target_colors[i], step, steps)
            pixels[i] = current_colors[i]
        pixels.show()
        time.sleep(0.01)

def set_leds(meditation):
    with lock:
        target_colors = [(255, 255, 255, 0)] * num_pixels  # Initialize target colors with baseline white

        # Determine the color based on meditation value
        level = analyze_meditation(meditation)
        start_color = color_levels[level]
        end_color = (255, 255, 255, 0)  # Transition to white

        if meditation <= 20:
            for i in range(22, 27):
                target_colors[i] = start_color
            for i in range(57, 61):
                target_colors[i] = start_color
        elif meditation <= 40:
            for i in range(22, 27):
                target_colors[i] = start_color
            for i in range(57, 61):
                target_colors[i] = start_color
            for i in range(27, 31):
                target_colors[i] = gradient_color(start_color, end_color, i-27, 3)
            for i in range(53, 57):
                target_colors[i] = gradient_color(start_color, end_color, i-53, 3)
        elif meditation <= 60:
            for i in range(22, 31):
                target_colors[i] = start_color
            for i in range(53, 61):
                target_colors[i] = start_color
            for i in range(31, 35):
                target_colors[i] = gradient_color(start_color, end_color, i-31, 3)
            for i in range(49, 53):
                target_colors[i] = gradient_color(start_color, end_color, i-49, 3)
        elif meditation <= 80:
            for i in range(22, 35):
                target_colors[i] = start_color
            for i in range(49, 61):
                target_colors[i] = start_color
            for i in range(35, 39):
                target_colors[i] = gradient_color(start_color, end_color, i-35, 3)
            for i in range(45, 49):
                target_colors[i] = gradient_color(start_color, end_color, i-45, 3)
        else:
            for i in range(22, 39):
                target_colors[i] = start_color
            for i in range(45, 61):
                target_colors[i] = start_color
            for i in range(39, 42):
                target_colors[i] = gradient_color(start_color, end_color, i-39, 2)
            for i in range(42, 45):
                target_colors[i] = gradient_color(start_color, end_color, i-42, 2)

        smooth_transition(target_colors)

def test_led_levels():
    test_meditation_levels = [10, 30, 50, 70, 90]  # Example meditation levels
    for level in test_meditation_levels:
        print(f"Testing meditation level: {level}")
        set_leds(level)
        time.sleep(5)  # Display each level for 5 seconds

try:
    # Start with all LEDs in white
    pixels.fill((255, 255, 255, 0))
    pixels.show()
    time.sleep(5)  # Display initial color for 5 seconds

    # Test each meditation level
    test_led_levels()
except KeyboardInterrupt:
    pixels.fill((0, 0, 0, 0))
    pixels.show()
    print("LED test terminated.")
