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

# Define color levels
color_levels = {
    1: (0, 0, 20, 0),   # very dark blue
    2: (0, 0, 60, 0),   # dark blue
    3: (0, 3, 90, 0),   # medium blue
    4: (0, 5, 120, 0), # light blue
    5: (0, 8, 250, 0)  # white
}

# Lock to prevent interference between LEDs  
lock = Lock()

# Initialize current state with off state for all LEDs
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

def apply_gradient_effect(level):
    start_color = color_levels[level]
    end_color = (255, 255, 255, 0)  # Transition to white

    # Initialize new state with low white light
    new_state = [(10, 10, 10, 0)] * num_pixels

    if level == 1:
        for i in range(22, 26):
            new_state[i] = gradient_color(start_color, end_color, 22 - i, 4)
        for i in range(57, 60):
            new_state[i] = gradient_color(start_color, end_color, i - 57, 3)
    elif level == 2:
        for i in range(22, 26):
            new_state[i] = start_color
        for i in range(57, 60):
            new_state[i] = start_color
        for i in range(27, 30):
            new_state[i] = gradient_color(start_color, end_color, i - 27, 3)
        for i in range(56, 53, -1):
            new_state[i] = gradient_color(start_color, end_color, 56 - i, 3)
    elif level == 3:
        for i in range(22, 30):
            new_state[i] = start_color
        for i in range(53, 60):
            new_state[i] = start_color
        for i in range(31, 34):
            new_state[i] = gradient_color(start_color, end_color, i - 31, 3)
        for i in range(52, 49, -1):
            new_state[i] = gradient_color(start_color, end_color, 52 - i, 3)
    elif level == 4:
        for i in range(22, 34):
            new_state[i] = start_color
        for i in range(49, 60):
            new_state[i] = start_color
        for i in range(35, 38):
            new_state[i] = gradient_color(start_color, end_color, i - 35, 3)
        for i in range(48, 45, -1):
            new_state[i] = gradient_color(start_color, end_color, 48 - i, 3)
    elif level == 5:
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

def run_test():
    try:
        for level in range(1, 6):  # Test all levels from 1 to 5
            print(f"Testing level {level}")
            apply_gradient_effect(level)
            time.sleep(5)  # Hold each level for 5 seconds
        print("Test completed.")
    except KeyboardInterrupt:
        print("Test interrupted.")
    finally:
        pixels.fill((0, 0, 0, 0))  # Turn off all LEDs
        pixels.show()

# Run the test
run_test()
