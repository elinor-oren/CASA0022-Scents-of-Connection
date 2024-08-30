import paho.mqtt.client as mqtt
import time
import RPi.GPIO as GPIO
import csv
from datetime import datetime
from threading import Timer, Lock, Thread
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
current_state_headset1 = [(0, 0, 0, 0)] * len(HEADSET1_LEDS)
current_state_headset2 = [(0, 0, 0, 0)] * len(HEADSET2_LEDS)

breathing_brightness = 0.1
breathing_direction = 1

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

def smooth_transition(new_colors, led_range, current_state, duration=0.1, interval=0.01):
    steps = int(duration / interval)
    for step in range(steps):
        for i, led_index in enumerate(led_range):
            if i < len(current_state) and i < len(new_colors):
                current_color = current_state[i]
                target_color = new_colors[i]
                intermediate_color = gradient_color(current_color, target_color, step, steps - 1)
                pixels[led_index] = intermediate_color
        pixels.show()
        time.sleep(interval)
    return new_colors

def calculate_gradient_effect_headset1(meditation):
    level = analyze_meditation(meditation)
    start_color = color_levels_teal[level]
    end_color = (255, 255, 255, 0)  # Transition to white

    new_state1 = [(10, 10, 10, 0)] * len(HEADSET1_LEDS)

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

    return new_state1

def calculate_gradient_effect_headset2(meditation):
    level = analyze_meditation(meditation)
    start_color = color_levels_tangerine[level]
    end_color = (255, 255, 255, 0)  # Transition to white

    new_state2 = [(10, 10, 10, 0)] * len(HEADSET2_LEDS)

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

    return new_state2

def check_very_high(participant):
    global meditation_count, rainbow_running
    with lock:
        if rainbow_running:
            return
        if all(count >= 3 for count in meditation_count.values()):
            if not rainbow_running:
                rainbow_running = True
                GPIO.output(17, GPIO.HIGH)
                duration = time.time() - start_time[participant]
                print(f"Very high state achieved for all participants in {duration} seconds")
                log_data(participant, "Very High Time", duration)
                for p in participants:
                    log_data(p, "Rainbow Wheel", "Started")

                rainbow_cycle(0.1, duration=10)

                GPIO.output(17, GPIO.LOW)
                for p in participants:
                    log_data(p, "Rainbow Wheel", "Ended")
                    log_data(p, "Script", "Terminated")

                pixels.fill((10, 10, 10, 0))
                pixels.show()
                print("Script terminating...")

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
    global headset_data, meditation_count, valid_packets_received, experiment_started, current_state_headset1, current_state_headset2
    payload = msg.payload.decode('utf-8')
    topic = msg.topic

    try:
        data = [int(i) for i in payload.split(',')]
        if "headset1" in topic:
            participant_index = participants[0]
        elif "headset2" in topic:
            participant_index = participants[1] if len(participants) > 1 else participants[0]
        else:
            print(f"Unknown topic {topic}")
            return

        if data[0] == 0:
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

            if all(count > 4 for count in valid_packets_received.values()) and not experiment_started:
                experiment_started = True
                for participant in participants:
                    log_data(participant, "Experiment", "Started")

            if experiment_started:
                meditation = headset_data[participant_index]["Meditation"]
                if participant_index == participants[0]:
                    new_state1 = calculate_gradient_effect_headset1(meditation)
                    current_state_headset1 = smooth_transition(new_state1, HEADSET1_LEDS, current_state_headset1, duration=0.1)
                elif participant_index == participants[1]:
                    new_state2 = calculate_gradient_effect_headset2(meditation)
                    current_state_headset2 = smooth_transition(new_state2, HEADSET2_LEDS, current_state_headset2, duration=0.1)

                if meditation >= very_high_threshold:
                    meditation_count[participant_index] += 1
                    if meditation_count[participant_index] == 1:
                        check_very_high(participant_index)
                else:
                    meditation_count[participant_index] = 0

    except ValueError:
        print("Failed to parse CSV")

def breathing_thread():
    global breathing_brightness, breathing_direction
    while True:
        breathing_brightness += 0.01 * breathing_direction
        if breathing_brightness >= 1.0 or breathing_brightness <= 0.1:
            breathing_direction *= -1
        time.sleep(0.05)

def rainbow_cycle(wait, duration):
    global rainbow_running
    start_time = time.time()
    while time.time() - start_time < duration:
        for j in range(255):
            for i in range(num_pixels):
                pixel_index = (i * 256 // num_pixels) + j
                pixels[i] = wheel(pixel_index & 255)
            pixels.show()
            time.sleep(wait)
    rainbow_running = False

def wheel(pos):
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

# Set up client
client = mqtt.Client()
client.username_pw_set("student", "ce2021-mqtt-forget-whale")
client.on_connect = on_connect
client.on_message = on_message

# Connect to broker
client.connect("mqtt.cetools.org", 1884, 60)

# Start the breathing effect in a separate thread
breathing_thread = Thread(target=breathing_thread)
breathing_thread.daemon = True
breathing_thread.start()

# Start MQTT loop
client.loop_start()

# Main loop
try:
    while True:
        if not rainbow_running:
            if not experiment_started:
                chaser_effect()
            else:
                # Apply breathing effect to non-gradient LEDs
                color = tuple(int(breathing_brightness * c) for c in warm_yellow)
                for i in range(1, 22):
                    pixels[i] = color
                pixels.show()
        time.sleep(0.01)  # Small delay to prevent excessive CPU usage
except KeyboardInterrupt:
    rainbow_running = False
    pixels.fill((0, 0, 0, 0))
    pixels.show()

    GPIO.cleanup()
    client.loop_stop()
    client.disconnect()
