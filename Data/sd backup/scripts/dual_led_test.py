#Dual LED test
import time
import board
import neopixel

# NeoPixel setup
pixel_pin = board.D18
num_pixels = 60
ORDER = neopixel.GRBW
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=1.0, auto_write=False, pixel_order=ORDER)

# Define LED ranges for each headset
HEADSET1_LEDS = range(22, 42)  # LEDs 22-41 for headset 1
HEADSET2_LEDS = range(42, 60)  # LEDs 42-60 for headset 2

# Define colors for each headset
color_levels_teal = {
    1: (0, 20, 20, 0),   # very dark teal
    2: (0, 60, 60, 0),   # dark teal
    3: (0, 80, 80, 0),   # medium teal
    4: (0, 100, 100, 0), # light teal
    5: (0, 200, 200, 0)  # white
}

color_levels_tangerine = {
    1: (100, 25, 0, 0),  # very dark tangerine
    2: (120, 40, 0, 0),  # dark tangerine
    3: (160, 65, 0, 0),  # medium tangerine
    4: (180, 85, 0, 0), # light tangerine
    5: (200, 105, 0, 0)  # lightest tangerine
}

current_state = [(0, 0, 0, 0)] * num_pixels  # Store the current state of all LEDs
rainbow_running = False  # This is to simulate the state check

def gradient_color(start_color, end_color, step, total_steps):
    """Interpolate between start_color and end_color."""
    return tuple(
        int(start_color[i] + (end_color[i] - start_color[i]) * (step / total_steps))
        for i in range(4)
    )

def smooth_transition(new_colors, led_range, duration=0.5, interval=0.05):
    global current_state
    steps = int(duration / interval)
    for step in range(steps):
        for i in range(len(led_range)):
            index = led_range[i]
            current_color = current_state[index]
            target_color = new_colors[i]
            intermediate_color = gradient_color(current_color, target_color, step, steps - 1)
            pixels[index] = intermediate_color
        pixels.show()
        time.sleep(interval)
    # Update the current state for the specific range
    for i in range(len(led_range)):
        current_state[led_range[i]] = new_colors[i]
        
def apply_gradient_effect_headset1(meditation):
    if rainbow_running:
        return  # Do not perform transition if rainbow cycle is running
    level = analyze_meditation(meditation)
    start_color = color_levels_teal[level]
    end_color = (255, 255, 255, 0)  # Transition to white

    new_state1 = [(10, 10, 10, 0)] * len(HEADSET1_LEDS)
    for i in range(len(HEADSET1_LEDS)):
        new_state1[i] = (10, 10, 10, 0)  # Apply low white light baseline

    if meditation <= 25:
        for i in range(22, 26):
            new_state1[i - 22] = start_color
    elif meditation <= 40:
        for i in range(22, 28):
            new_state1[i - 22] = start_color
        for i in range(28, 31):
            new_state1[i - 22] = gradient_color(start_color, end_color, i - 28, 3)
    elif meditation <= 60:
        for i in range(22, 32):
            new_state1[i - 22] = start_color
        for i in range(32, 35):
            new_state1[i - 22] = gradient_color(start_color, end_color, i - 32, 3)
    elif meditation <= 80:
        for i in range(22, 36):
            new_state1[i - 22] = start_color
        for i in range(36, 39):
            new_state1[i - 22] = gradient_color(start_color, end_color, i - 36, 3)
    else:
        for i in range(22, 39):
            new_state1[i - 22] = start_color
        for i in range(39, 42):
            new_state1[i - 22] = gradient_color(start_color, end_color, i - 39, 3)

    smooth_transition(new_state1, HEADSET1_LEDS)

def apply_gradient_effect_headset2(meditation):
    if rainbow_running:
        return  # Do not perform transition if rainbow cycle is running
    level = analyze_meditation(meditation)
    start_color = color_levels_tangerine[level]
    end_color = (255, 255, 255, 0)  # Transition to white

    new_state2 = [(10, 10, 10, 0)] * len(HEADSET2_LEDS)
    for i in range(len(HEADSET2_LEDS)):
        new_state2[i] = (10, 10, 10, 0)  # Apply low white light baseline

    if meditation <= 25:
        for i in range(58, 60):
            new_state2[i - 42] = start_color
    elif meditation <= 40:
        for i in range(58, 60):
            new_state2[i - 42] = start_color
        for i in range(57, 54, -1):
            new_state2[i - 42] = gradient_color(start_color, end_color, 57 - i, 3)
    elif meditation <= 60:
        for i in range(53, 60):
            new_state2[i - 42] = start_color
        for i in range(52, 49, -1):
            new_state2[i - 42] = gradient_color(start_color, end_color, 52 - i, 3)
    elif meditation <= 80:
        for i in range(49, 60):
            new_state2[i - 42] = start_color
        for i in range(48, 45, -1):
            new_state2[i - 42] = gradient_color(start_color, end_color, 48 - i, 3)
    else:
        for i in range(45, 60):
            new_state2[i - 42] = start_color
        for i in range(44, 42, -1):
            new_state2[i - 42] = gradient_color(start_color, end_color, 44 - i, 2)

    smooth_transition(new_state2, HEADSET2_LEDS)

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

# Test the LED functions
def test_led_functions():
    print("Testing LED functions...")

    # Test Headset 1
    for meditation in [20, 35, 55, 75, 85]:
        print(f"Testing Headset 1 with meditation level: {meditation}")
        apply_gradient_effect_headset1(meditation)
        time.sleep(2)

    # Test Headset 2
    for meditation in [20, 35, 55, 75, 85]:
        print(f"Testing Headset 2 with meditation level: {meditation}")
        apply_gradient_effect_headset2(meditation)
        time.sleep(2)

    print("LED functions tested.")

if __name__ == "__main__":
    test_led_functions()
