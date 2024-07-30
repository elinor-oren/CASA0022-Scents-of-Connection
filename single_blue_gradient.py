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

