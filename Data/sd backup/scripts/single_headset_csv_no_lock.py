#single_headset_csv_no_lock.py
import paho.mqtt.client as mqtt
import time
import RPi.GPIO as GPIO
import csv
from threading import Timer
from datetime import datetime
import board
import neopixel
import math
from threading import Lock  # Import the Lock class

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)

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
tangerine = (255, 80, 0, 0)  # Tangerine orange color
teal = (0, 128, 128, 0)  # Turquoisey blue color
warm_yellow = (255, 150, 0, 0)  # Warm yellow color

# Variables
participant = input("Enter participant number: ")
headset_data = None
meditation_count = 0
start_time = time.time()
very_high_threshold = 30
valid_packets_received = 0  # Counter for received packets with signal strength of 0
experiment_started = False  # Flag to indicate experiment start
rainbow_running = False  # Flag to indicate the rainbow led effect
lock = Lock()  # Lock to prevent interference between LEDs
current_state = [(0, 0, 0, 0)] * (num_pixels - 22)  # Store the current state of LEDs

# CSV file setup
csv_file = f'{participant}_single_data_{datetime.now().strftime("%d_%m_%Y_%H%M")}.csv'
with open(csv_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Timestamp", "Participant", "Headset", "Signal Strength", "Attention", "Meditation", 
                     "Delta", "Theta", "Low Alpha", "High Alpha", "Low Beta", "High Beta", "Low Gamma", "High Gamma", "Very High Time", "Very High Duration"])

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

# Loop LED effects
def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colors are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    if pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    pos -= 170
    return (pos * 3, 0, 255 - pos * 3)

def rainbow_cycle(wait):
    global rainbow_running
    with lock:
        rainbow_running = True
        for j in range(255):
            for i in range(22, 60):
                pixel_index = (i * 256 // num_pixels) + j
                pixels[i] = wheel(pixel_index & 255)
            pixels.show()
            time.sleep(wait)
        rainbow_running = False

# Gradient and glow effects
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
        if 22 <= index < num_pixels:  # Ensure we stay within range
            pixels[index] = color
    pixels.show()

def fixed_low_glow(start, end, color):
    for i in range(start, min(end + 1, num_pixels)):
        pixels[i] = color
    pixels.show()

def fade_out_effect(start_led, end_led, steps=20):
    """Fade out the LEDs between start_led and end_led."""
    for step in range(steps):
        for i in range(start_led, end_led + 1):
            if 0 <= i < num_pixels:  # Ensure we stay within range
                current_color = pixels[i]
                color = gradient_color(current_color, (0, 0, 0, 0), step, steps - 1)
                pixels[i] = color
        pixels.show()
        time.sleep(0.01)
def apply_gradient_effect(meditation):
    global current_state
    level = analyze_meditation(meditation)
    start_color = color_levels[level]
    end_color = (255, 255, 255, 0)  # Transition to white

    # Initialize new state with low white light
    new_state = [(10, 10, 10, 0)] * (num_pixels - 22)
    for i in range(22, 60):
        new_state[i - 22] = (10, 10, 10, 0)  # Apply low white light baseline

    if meditation <= 25:
        for i in range(22, 26):
            new_state[i - 22] = start_color
        for i in range(57, 60):
            new_state[i - 22] = start_color
    elif meditation <= 40:
        for i in range(22, 26):
            new_state[i - 22] = start_color
        for i in range(57, 60):
            new_state[i - 22] = start_color
        for i in range(27, 30):
            new_state[i - 22] = gradient_color(start_color, end_color, i - 27, 3)
        for i in range(56, 53, -1):
            new_state[i - 22] = gradient_color(start_color, end_color, 56 - i, 3)
    elif meditation <= 60:
        for i in range(22, 30):
            new_state[i - 22] = start_color
        for i in range(53, 60):
            new_state[i - 22] = start_color
        for i in range(31, 34):
            new_state[i - 22] = gradient_color(start_color, end_color, i - 31, 3)
        for i in range(52, 49, -1):
            new_state[i - 22] = gradient_color(start_color, end_color, 52 - i, 3)
    elif meditation <= 80:
        for i in range(22, 34):
            new_state[i - 22] = start_color
        for i in range(49, 60):
            new_state[i - 22] = start_color
        for i in range(35, 38):
            new_state[i - 22] = gradient_color(start_color, end_color, i - 35, 3)
        for i in range(48, 45, -1):
            new_state[i - 22] = gradient_color(start_color, end_color, 48 - i, 3)
    else:
        for i in range(22, 38):
            new_state[i - 22] = start_color
        for i in range(45, 60):
            new_state[i - 22] = start_color
        for i in range(39, 41):
            new_state[i - 22] = gradient_color(start_color, end_color, i - 39, 2)
        for i in range(44, 42, -1):
            new_state[i - 22] = gradient_color(start_color, end_color, 44 - i, 2)

    # Apply smooth transition to the new state
    smooth_transition(new_state)

## Removed due to index error
# def apply_gradient_effect(meditation):
#     global current_state
#     level = analyze_meditation(meditation)
#     start_color = color_levels[level]
#     end_color = (255, 255, 255, 0)  # Transition to white

#     # Initialize new state with low white light
#     new_state = [(10, 10, 10, 0)] * (num_pixels - 22)
#     for i in range(22, 60):
#         new_state[i-22] = (10, 10, 10, 0)  # Apply low white light baseline

#     # # Initialize new state with low white light
#     # new_state = current_state[:]  # Start with the current state
#     # for i in range(22, 61):
#     #     new_state[i-22] = (10, 10, 10, 0)  # Apply low white light baseline

#     if meditation <= 25:
#         for i in range(22, 26):
#             new_state[i] = start_color
#         for i in range(57, 60):
#             new_state[i] = start_color
#     elif meditation <= 40:
#         for i in range(22, 26):
#             new_state[i] = start_color
#         for i in range(57, 60):
#             new_state[i] = start_color
#         for i in range(27, 30):
#             new_state[i] = gradient_color(start_color, end_color, i - 27, 3)
#         for i in range(56, 53, -1):
#             new_state[i] = gradient_color(start_color, end_color, 56 - i, 3)
#     elif meditation <= 60:
#         for i in range(22, 30):
#             new_state[i] = start_color
#         for i in range(53, 60):
#             new_state[i] = start_color
#         for i in range(31, 34):
#             new_state[i] = gradient_color(start_color, end_color, i - 31, 3)
#         for i in range(52, 49, -1):
#             new_state[i] = gradient_color(start_color, end_color, 52 - i, 3)
#     elif meditation <= 80:
#         for i in range(22, 34):
#             new_state[i] = start_color
#         for i in range(49, 60):
#             new_state[i] = start_color
#         for i in range(35, 38):
#             new_state[i] = gradient_color(start_color, end_color, i - 35, 3)
#         for i in range(48, 45, -1):
#             new_state[i] = gradient_color(start_color, end_color, 48 - i, 3)
#     else:
#         for i in range(22, 38):
#             new_state[i] = start_color
#         for i in range(45, 60):
#             new_state[i] = start_color
#         for i in range(39, 41):
#             new_state[i] = gradient_color(start_color, end_color, i - 39, 2)
#         for i in range(44, 42, -1):
#             new_state[i] = gradient_color(start_color, end_color, 44 - i, 2)

    # # Apply smooth transition to the new state
    # smooth_transition(new_state)

def smooth_transition(new_colors, duration=0.5, interval=0.05):
    global current_state
    steps = int(duration / interval)
    for step in range(steps):
        for i in range(22, 61):
            index = i - 22
            if index < len(current_state):
                # Interpolate between current color and target color
                current_color = current_state[index]
                target_color = new_colors[index]
                intermediate_color = gradient_color(current_color, target_color, step, steps - 1)
                pixels[i] = intermediate_color
        pixels.show()
        time.sleep(interval)
    # Update the current state for LEDs 22-60
    current_state = new_colors

''' removed because I worried that smooth transition was interfering with the breathing effect
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
'''

# Base LED effects
def chaser_effect():
    for i in range(1, 21):
        pixels.fill((0, 0, 0, 0))
        pixels[i] = teal
        pixels.show()
        time.sleep(0.05)
        pixels[i] = (0, 0, 0, 0)
    pixels.show()

def blink_leds(times, interval):
    for _ in range(times):
        for i in range(1, 21):
            pixels[i] = teal
        pixels.show()
        time.sleep(interval)
        for i in range(1, 21):
            pixels[i] = (0, 0, 0, 0)
        pixels.show()
        time.sleep(interval)

def exaggerated_breathing_effect(times, interval):
    steps = 400  # Number of steps for breathing effect
    hold_time = 2  # Hold time at peak and minimum brightness
    min_brightness = 0.1  # Minimum brightness level
    max_brightness = 1.0  # Maximum brightness level

    for _ in range(times):
        # Breathe in
        for step in range(steps):
            brightness = min_brightness + (max_brightness - min_brightness) * (step / float(steps))
            color = tuple(int(brightness * c) for c in warm_yellow)
            for i in range(1, 22):
                pixels[i] = color
            pixels.show()
            time.sleep(interval / (2 * steps))

        time.sleep(hold_time)  # Hold at peak brightness

        # Breathe out
        for step in range(steps):
            brightness = max_brightness - (max_brightness - min_brightness) * (step / float(steps))
            color = tuple(int(brightness * c) for c in warm_yellow)
            for i in range(1, 22):
                pixels[i] = color
            pixels.show()
            time.sleep(interval / (1.5 * steps))  # Make breathe out more gradual

        time.sleep(hold_time)  # Hold at minimum brightness

def check_very_high():
    global meditation_count, start_time
    if meditation_count >= 5:
        GPIO.output(17, GPIO.HIGH)
        duration = time.time() - start_time
        print(f"Very high state achieved in {duration} seconds")
        log_data("Very High Time", duration)
        log_data("Rainbow Wheel", "Started")
        rainbow_cycle(0.1)  # Trigger rainbow wheel effect
        log_data("Rainbow Wheel", "Ended")
        pixels.fill((0, 0, 0, 0))  # Turn off all LEDs for 1 second after the rainbow effect
        pixels.show()
        time.sleep(1)
    else:
        Timer(1, check_very_high).start()

def log_data(key, value):
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        if isinstance(value, dict):
            row = [datetime.now(), participant] + list(value.values())
            writer.writerow(row)
        else:
            writer.writerow([datetime.now(), participant, key, value])

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("student/ucbvren/headsets/#")

def on_message(client, userdata, msg):
    global headset_data, meditation_count, start_time, valid_packets_received, experiment_started
    payload = msg.payload.decode('utf-8')
    topic = msg.topic

    try:
        data = [int(i) for i in payload.split(',')]
        if data[0] == 0:  # Check if signal strength is 0
            valid_packets_received += 1
            headset_data = {
                "Signal Strength": data[0],
                "Attention": data[1],
                "Meditation": data[2],
                "Delta": data[3],
                "Theta": data[4],
                "Low Alpha": data[5],
                "High Alpha": data[6],
                "Low Beta": data[7],
                "High Beta": data[8],
                "Low Gamma": data[9],
                "High Gamma": data[10]
            }
            log_data("headset", headset_data)
    except ValueError:
        print("Failed to parse CSV")
        return

    if valid_packets_received >4 and not experiment_started:
        experiment_started = True
        log_data("Experiment", "Started")
        blink_leds(1, 1)  # Signal that the experiment has started with a slow blink
        exaggerated_breathing_effect(1, 7)  # Maintain a breathing effect once the experiment has started
        pixels.fill((0, 0, 0, 0))
        pixels.show()

    if headset_data and experiment_started:
        meditation = headset_data["Meditation"]
        apply_gradient_effect(meditation)
        if meditation >= very_high_threshold:
            meditation_count += 1
            if meditation_count == 1:
                start_time = time.time()
                check_very_high()
        else:
            meditation_count = 0
            GPIO.output(17, GPIO.LOW)

# Set up client
client = mqtt.Client()
client.username_pw_set("student", "ce2021-mqtt-forget-whale")
client.on_connect = on_connect
client.on_message = on_message

# Connect to broker
client.connect("mqtt.cetools.org", 1884, 60)

# Blocking call that processes network traffic, dispatches callbacks and handles reconnecting.
client.loop_start()

# Keep the script running
try:
    while True:
        if valid_packets_received <= 3:
            chaser_effect()
        elif experiment_started:
            exaggerated_breathing_effect(1, 7)  # Slow breathing effect after the experiment has started
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()
    client.loop_stop()
    client.disconnect()
