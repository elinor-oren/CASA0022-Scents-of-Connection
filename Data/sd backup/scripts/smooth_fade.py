import time
import board
import neopixel
import math

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

dim_yellowy_white = (100, 100, 40, 0)  # Dimmer yellowy white color for background
current_colors = [dim_yellowy_white] * num_pixels  # Initialize all LEDs with dim baseline white

def gradient_color(start_color, end_color, step, total_steps):
    """Interpolate between start_color and end_color."""
    return tuple(
        int(start_color[i] + (end_color[i] - start_color[i]) * (step / total_steps))
        for i in range(4)
    )

def smooth_transition(target_colors, steps=50):
    global current_colors
    for step in range(steps):
        for i in range(num_pixels):
            current_colors[i] = gradient_color(current_colors[i], target_colors[i], step, steps)
            pixels[i] = current_colors[i]
        pixels.show()
        time.sleep(0.01)

def set_leds(level):
    target_colors = [dim_yellowy_white] * num_pixels  # Initialize target colors with dim baseline white

    # Determine the color based on meditation value
    start_color = color_levels[level]
    end_color = dim_yellowy_white  # Transition to dim white

    if level == 1:
        for i in range(22, 27):
            target_colors[i] = start_color
        for i in range(57, 60):
            target_colors[i] = start_color
    elif level == 2:
        for i in range(22, 27):
            target_colors[i] = start_color
        for i in range(57, 60):
            target_colors[i] = start_color
        for i in range(27, 31):
            target_colors[i] = gradient_color(start_color, end_color, i-27, 3)
        for i in range(53, 57):
            target_colors[i] = gradient_color(start_color, end_color, i-53, 3)
    elif level == 3:
        for i in range(22, 31):
            target_colors[i] = start_color
        for i in range(49, 53):
            target_colors[i] = start_color
        for i in range(31, 35):
            target_colors[i] = gradient_color(start_color, end_color, i-31, 3)
        for i in range(45, 49):
            target_colors[i] = gradient_color(start_color, end_color, i-45, 3)
    elif level == 4:
        for i in range(22, 35):
            target_colors[i] = start_color
        for i in range(45, 49):
            target_colors[i] = start_color
        for i in range(35, 39):
            target_colors[i] = gradient_color(start_color, end_color, i-35, 3)
        for i in range(41, 45):
            target_colors[i] = gradient_color(start_color, end_color, i-41, 3)
    elif level == 5:
        for i in range(22, 39):
            target_colors[i] = start_color
        for i in range(42, 45):
            target_colors[i] = start_color
        for i in range(39, 42):
            target_colors[i] = gradient_color(start_color, end_color, i-39, 2)
        for i in range(45, 49):
            target_colors[i] = gradient_color(start_color, end_color, i-45, 3)

    smooth_transition(target_colors)

try:
    while True:
        for level in range(1, 6):
            print(f"Setting LEDs for meditation level {level}")
            set_leds(level)
            time.sleep(5)  # Pause for 5 seconds to observe each level's effect
except KeyboardInterrupt:
    pixels.fill((0, 0, 0, 0))
    pixels.show()
    print("Test script terminated.")
