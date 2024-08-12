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

# Dual script - Define LED ranges for each headset
HEADSET1_LEDS = range(22, 42)  # LEDs 22-41 for headset 1
HEADSET2_LEDS = range(42, 60)  # LEDs 42-60 for headset 2

# Single - Define colors
color_levels = {
    1: (0, 0, 20, 0),   # very dark blue
    2: (0, 0, 60, 0),   # dark blue
    3: (0, 3, 90, 0),   # medium blue
    4: (0, 5, 120, 0),  # light blue
    5: (0, 8, 250, 0)   # white
}

# Dual - Define colors for each headset
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
    4: (180, 85, 0, 0),  # light tangerine
    5: (200, 105, 0, 0)  # lightest tangerine
}

current_state = [(0, 0, 0, 0)] * num_pixels  # Start with all LEDs off
lock = Lock()  # Lock to prevent interference between LEDs

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

# Single 
def smooth_transition(new_colors, duration=0.01, interval=0.001):
    global current_state
    steps = int(duration / interval)
    for step in range(steps):
        for i in range(len(new_colors)):
            if i < num_pixels:
                current_color = current_state[i]
                target_color = new_colors[i]
                intermediate_color = gradient_color(current_color, target_color, step, steps - 1)
                pixels[i] = intermediate_color
        pixels.show()
        time.sleep(interval)
    current_state = new_colors

def apply_gradient_effect(meditation):
    with lock:
        level = analyze_meditation(meditation)
        start_color = color_levels[level]
        end_color = (255, 255, 255, 0)  # Transition to white

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
                new_state[i] = gradient_color(start_color, end_color, i - 27, 3)
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

        smooth_transition(new_state)

# Dual 
def smooth_transition_dual(new_colors, led_range, duration=0.5, interval=0.05):
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
    for i in range(len(led_range)):
        current_state[led_range[i]] = new_colors[i]
        
def apply_gradient_effect_headset1(meditation):
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

    smooth_transition_dual(new_state1, HEADSET1_LEDS)

def apply_gradient_effect_headset2(meditation):
    level = analyze_meditation(meditation)
    start_color = color_levels_tangerine[level]
    end_color = (255, 255, 255, 0)  # Transition to white

    new_state2 = [(10, 10, 10, 0)] * len(HEADSET2_LEDS)
    for i in range(len(HEADSET2_LEDS)):
        new_state2[i] = (10, 10, 10, 0)  # Apply low white light baseline

    if meditation <= 25:
        for i in range(56, 60):
            new_state2[i - 42] = start_color
    elif meditation <= 40:  # Level 2
        for i in range(55, 60):  # Changed from 56 to 55
            new_state2[i - 42] = start_color
        for i in range(54, 52, -1):  # Changed from 55,53 to 54,52
            new_state2[i - 42] = gradient_color(start_color, end_color, 55 - i, 3)
    elif meditation <= 60:
        for i in range(51, 60):
            new_state2[i - 42] = start_color
        for i in range(50, 48, -1):
            new_state2[i - 42] = gradient_color(start_color, end_color, 51 - i, 3)
    elif meditation <= 80:
        for i in range(47, 60):
            new_state2[i - 42] = start_color
        for i in range(46, 44, -1):
            new_state2[i - 42] = gradient_color(start_color, end_color, 47 - i, 3)
    else:
        for i in range(43, 60):
            new_state2[i - 42] = start_color
        new_state2[42 - 42] = start_color  # Add one more LED in tangerine instead of gradient

    smooth_transition_dual(new_state2, HEADSET2_LEDS)


def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (r, g, b, 0)

def rainbow_cycle(wait):
    for j in range(255):
        for i in range(num_pixels):
            pixel_index = (i * 256 // num_pixels) + j
            pixels[i] = wheel(pixel_index & 255)
        pixels.show()
        time.sleep(wait)

# Test the LED functions
def test_led_functions():
    print("Testing Single LED effects...")
    for meditation in [20, 35, 55, 75, 85]:
        print(f"Testing Single LED effect with meditation level: {meditation}")
        apply_gradient_effect(meditation)
        time.sleep(2)

    print("\nTesting Dual LED effects...")
    for meditation in [20, 35, 55, 75, 85]:
        print(f"Testing Dual LED effects with meditation level: {meditation}")
        apply_gradient_effect_headset1(meditation)
        apply_gradient_effect_headset2(meditation)
        time.sleep(2)

    print("\nTesting Rainbow Wheel effect...")
    for _ in range(2):  # Run rainbow cycle twice
        rainbow_cycle(0.01)  # Very fast cycle

    print("LED functions tested.")

if __name__ == "__main__":
    try:
        test_led_functions()
    except KeyboardInterrupt:
        pixels.fill((0, 0, 0, 0))
        pixels.show()
        print("LED test script terminated.")