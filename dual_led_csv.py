import paho.mqtt.client as mqtt
import time
import RPi.GPIO as GPIO
import csv
from datetime import datetime
from threading import Timer, Lock
import board
import neopixel
import json

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)

# NeoPixel setup
pixel_pin = board.D18
num_pixels = 60
ORDER = neopixel.GRBW
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=1.0, auto_write=False, pixel_order=ORDER)

# Define LED ranges for each headset
HEADSET1_LEDS = range(22, 42)  # LEDs 22-41 for headset 1
HEADSET2_LEDS = range(42, 61)  # LEDs 42-60 for headset 2

# Define colors for each headset
color_levels_teal = {
    1: (0, 20, 20, 0),   # very dark teal
    2: (0, 60, 60, 0),   # dark teal
    3: (0, 80, 80, 0),   # medium teal
    4: (0, 100, 100, 0), # light teal
    5: (0, 200, 200, 0)  # white
}

color_levels_tangerine = {
    1: (255, 20, 0, 0),  # very dark tangerine
    2: (255, 60, 0, 0),  # dark tangerine
    3: (255, 80, 0, 0),  # medium tangerine
    4: (255, 100, 0, 0), # light tangerine
    5: (255, 140, 0, 0)  # lightest tangerine
}

# Variables
participants = input("Enter participant numbers (comma separated): ").split(',')
headset_data = {participant: None for participant in participants}
meditation_count = {participant: 0 for participant in participants}
start_time = {participant: time.time() for participant in participants}
very_high_threshold = 81
rainbow_running = False
lock = Lock()
current_state = [(0, 0, 0, 0)] * (num_pixels - 22)  # Store the current state of LEDs

# CSV file setup
csv_files = {participant: f'{participant}_single_data_{datetime.now().strftime("%d_%m_%Y_%H%M")}.csv' for participant in participants}
for participant, csv_file in csv_files.items():
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Participant", "Headset", "Signal Strength", "Attention", "Meditation", 
                         "Delta", "Theta", "Low Alpha", "High Alpha", "Low Beta", "High Beta", "Low Gamma", "High Gamma", "Very High Time"])

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

def smooth_transition(new_colors, led_range, duration=0.5, interval=0.05):
    global current_state
    steps = int(duration / interval)
    for step in range(steps):
        for i in led_range:
            index = i - led_range.start
            if index < len(current_state):
                current_color = current_state[index]
                target_color = new_colors[index]
                intermediate_color = gradient_color(current_color, target_color, step, steps - 1)
                pixels[i] = intermediate_color
        pixels.show()
        time.sleep(interval)
    # Update the current state for the specific range
    current_state[led_range.start - 22:led_range.start - 22 + len(new_colors)] = new_colors

def check_very_high(participant):
    global meditation_count
    if meditation_count[participant] >= 5:
        GPIO.output(17, GPIO.HIGH)
        duration = time.time() - start_time[participant]
        print(f"Very high state achieved for {participant} in {duration} seconds")
        log_data(participant, "Very High Time", duration)
        rainbow_cycle(0.1, duration=10)
        GPIO.output(17, GPIO.LOW)
        log_data("Rainbow Wheel", "Ended")
        pixels.fill((10, 10, 10, 0))
        pixels.show()
        print("Script terminating...")
        log_data("Script", "Terminated")
        GPIO.cleanup()
        client.loop_stop()
        client.disconnect()
        exit(0)
    else:
        Timer(1, check_very_high, args=[participant]).start()

def log_data(participant, key, value):
    csv_file = csv_files[participant]
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
    global headset_data, meditation_count
    payload = msg.payload.decode('utf-8')
    topic = msg.topic

    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        print("Failed to parse JSON")
        return

    if "headset1" in topic:
        headset_data[participants[0]] = data
        log_data(participants[0], "headset1", data)
    elif "headset2" in topic:
        headset_data[participants[1] if len(participants) > 1 else participants[0]] = data
        log_data(participants[1] if len(participants) > 1 else participants[0], "headset2", data)

    if all(headset_data.values()):
        for i, participant in enumerate(participants):
            headset = headset_data[participant]
            meditation = headset["Meditation"]
            if i == 0:
                apply_gradient_effect_headset1(meditation)
            elif i == 1:
                apply_gradient_effect_headset2(meditation)
            if meditation >= very_high_threshold:
                meditation_count[participant] += 1
                if meditation_count[participant] == 1:
                    check_very_high(participant)
            else:
                meditation_count[participant] = 0

def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colors are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    else:
        pos -= 170
        return (pos * 3, 0, 255 - pos * 3)

# Set up client
client = mqtt.Client()
client.username_pw_set("student", "XYZ")
client.on_connect = on_connect
client.on_message = on_message

# Connect to broker
client.connect("mqtt.cetools.org", 1884, 60)

# Blocking call that processes network traffic, dispatches callbacks and handles reconnecting.
client.loop_start()

# Keep the script running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()
    client.loop_stop()
    client.disconnect()
