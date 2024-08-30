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

# Define current state for smooth transitions
current_state = [(0, 0, 0, 0)] * num_pixels

def gradient_color(start_color, end_color, step, total_steps):
    """Interpolate between start_color and end_color."""
    return tuple(
        int(start_color[i] + (end_color[i] - start_color[i]) * (step / total_steps))
        for i in range(4)
    )

def smooth_transition(new_colors, duration=0.5, interval=0.05):
    global current_state
    steps = int(duration / interval)
    for step in range(steps):
        for i in range(len(new_colors)):
            if i < num_pixels:
                # Interpolate between current color and target color
                current_color = current_state[i]
                target_color = new_colors[i]
                intermediate_color = gradient_color(current_color, target_color, step, steps - 1)
                pixels[i] = intermediate_color
        pixels.show()
        time.sleep(interval)
    # Update the current state
    current_state = new_colors

def apply_gradient_effect(meditation):
    level = analyze_meditation(meditation)
    start_color = color_levels[level]
    end_color = (255, 255, 255, 0)  # Transition to white

    # Initialize new state with low white light
    new_state = [(10, 10, 10, 0)] * num_pixels

    if meditation <= 25:
        for i in range(22, 26):
            new_state[i] = start_color
        for i in range(57, 60):
            new_state[i] = start_color
    elif meditation <= 40:
        for i in range(22, 26):
            new_state[i] = start_color
        for i in range(57, 60):
            new_state[i] = start_color
        for i in range(27, 30):
            new_state[i] = gradient_color(start_color, end_color, i - 30, 3)
        for i in range(56, 53, -1):
            new_state[i] = gradient_color(start_color, end_color, 56 - i, 3)
    elif meditation <= 60:
        for i in range(22, 30):
            new_state[i] = start_color
        for i in range(53, 60):
            new_state[i] = start_color
        for i in range(31, 34):
            new_state[i] = gradient_color(start_color, end_color, i - 31, 3)
        for i in range(52, 49, -1):
            new_state[i] = gradient_color(start_color, end_color, 52 - i, 3)
    elif meditation <= 80:
        for i in range(22, 34):
            new_state[i] = start_color
        for i in range(49, 60):
            new_state[i] = start_color
        for i in range(35, 38):
            new_state[i] = gradient_color(start_color, end_color, i - 35, 3)
        for i in range(48, 45, -1):
            new_state[i] = gradient_color(start_color, end_color, 48 - i, 3)
    else:
        for i in range(22, 38):
            new_state[i] = start_color
        for i in range(45, 60):
            new_state[i] = start_color
        for i in range(39, 41):
            new_state[i] = gradient_color(start_color, end_color, i - 39, 2)
        for i in range(44, 42, -1):
            new_state[i] = gradient_color(start_color, end_color, 44 - i, 2)

    # Apply the smooth transition to the new state
    smooth_transition(new_state)

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

# Test script
try:
    while True:
        meditation = int(input("Enter a meditation level (0-100) to test LED effects: "))
        apply_gradient_effect(meditation)
except KeyboardInterrupt:
    pixels.fill((0, 0, 0, 0))
    pixels.show()
    print("Test terminated.")
