import paho.mqtt.client as mqtt 
import time 
import RPi.GPIO as GPIO 
import csv 
from datetime import datetime 
from threading import Timer, Lock 
import board 
import neopixel

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
HEADSET2_LEDS = range(42, 60)  # LEDs 42-60 for headset 2

# Define colors 
yellowy_white = (255, 255, 100, 0)  # Yellowy white color
tangerine = (255, 80, 0, 0)  # Tangerine orange color
teal = (0, 128, 128, 0)  # Turquoisey blue color
warm_yellow = (255, 150, 0, 0)  # Warm yellow color

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
valid_packets_received = {participant: 0 for participant in participants}
very_high_threshold = 81
experiment_started = False
rainbow_running = False
lock = Lock()
current_state = [(0, 0, 0, 0)] * (num_pixels - 22)  # Store the current state of LEDs

# CSV file setup
csv_files = {participant: f'{participant}_dual_data_{datetime.now().strftime("%d_%m_%Y_%H%M")}.csv' for participant in participants}
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
        for i in range(39, 41):
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

# Modified to ensure the rainbow only goes off when both the participants have reached the threshold
def check_very_high(participant):
    global meditation_count
    # Check if both participants have reached the meditation count of 5
    if all(count >= 5 for count in meditation_count.values()):
        GPIO.output(17, GPIO.HIGH)
        duration = time.time() - start_time[participant]
        print(f"Very high state achieved for all participants in {duration} seconds")
        log_data(participant, "Very High Time", duration)
        log_data("Rainbow Wheel", "Started")

        # Trigger rainbow wheel effect with GPIO17 on for 10 seconds
        rainbow_cycle(0.1, duration=10)

        # Turn off GPIO17 and log the end of the rainbow wheel
        GPIO.output(17, GPIO.LOW)
        log_data("Rainbow Wheel", "Ended")

        pixels.fill((10, 10, 10, 0))  # Set pixels to baseline white
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
    global headset_data, meditation_count, valid_packets_received, experiment_started
    payload = msg.payload.decode('utf-8')
    topic = msg.topic

    try:
        # Parse CSV data
        data = [int(i) for i in payload.split(',')]
        # Distinguish which participant/headset the data belongs to
        if "headset1" in topic:
            participant_index = participants[0]  # Assuming participants[0] is for headset 1
        elif "headset2" in topic:
            participant_index = participants[1] if len(participants) > 1 else participants[0]  # Ensure this logic fits your setup
        else:
            print(f"Unknown topic {topic}")
            return

        if data[0] == 0:  # Assuming valid data has 'Signal Strength' of 0
            valid_packets_received[participant_index] += 1
            headset_data[participant_index] = {
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
            log_data(participant_index, "headset", headset_data[participant_index])
    except ValueError:
        print("Failed to parse CSV")

    # Check if the experiment should start
    if all(count > 4 for count in valid_packets_received.values()) and not experiment_started:
        experiment_started = True
        log_data(participants[0], "Experiment", "Started")  # Corrected: Added participant argument
        # blink_leds(1, 1)  # Signal that the experiment has started with a slow blink
        exaggerated_breathing_effect(1, 7)  # Maintain a breathing effect once the experiment has started
        pixels.fill((0, 0, 0, 0))
        pixels.show()

    if headset_data and experiment_started:
        for i, participant in enumerate(participants):
            headset = headset_data.get(participant)
            if headset:
                meditation = headset.get("Meditation", 0)
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
        if not experiment_started:
            chaser_effect()
        elif experiment_started:
            exaggerated_breathing_effect(1, 7)  # Slow breathing effect after the experiment has started
        time.sleep(1)
except KeyboardInterrupt:
    pixels.fill((0, 0, 0, 0))
    pixels.show()

    GPIO.cleanup()
    client.loop_stop()
    client.disconnect()
