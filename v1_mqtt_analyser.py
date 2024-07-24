import paho.mqtt.client as mqtt
import json
import time
import RPi.GPIO as GPIO
import csv
from threading import Timer
from datetime import datetime

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)

# Variables
participants = input("Enter participant numbers (comma separated): ").split(',')
single_mode = len(participants) == 1
headset1_data = None
headset2_data = None
meditation_count = {participant: 0 for participant in participants}
start_time = {participant: time.time() for participant in participants}
very_high_threshold = 81

# CSV file setup
csv_file = f'headset_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
with open(csv_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Timestamp", "Participant", "Headset", "Signal Strength", "Attention", "Meditation", 
                     "Delta", "Theta", "Low Alpha", "High Alpha", "Low Beta", "High Beta", "Low Gamma", "High Gamma", "Very High Time"])

def analyze_meditation(meditation):
    if meditation <= 20:
        return 1  # very low
    elif meditation <= 40:
        return 2  # slightly low
    elif meditation <= 60:
        return 3  # natural state
    elif meditation <= 80:
        return 4  # slightly high
    else:
        return 5  # very high

def set_leds(meditation):
    led_count = analyze_meditation(meditation)
    # Code to illuminate LEDs based on led_count
    print(f"Illuminating {led_count} LEDs for meditation level {meditation}")

def check_very_high(participant, headset):
    global meditation_count
    if meditation_count[participant] >= 5:
        GPIO.output(17, GPIO.HIGH)
        duration = time.time() - start_time[participant]
        print(f"Very high state achieved for {participant} in {duration} seconds")
        log_data(participant, headset, "Very High Time", duration)
    else:
        Timer(1, check_very_high, args=[participant, headset]).start()

def log_data(participant, headset, key, value):
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now(), participant, headset, key, value])

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("student/ucbvren/headsets/#")

def on_message(client, userdata, msg):
    global headset1_data, headset2_data, single_mode, meditation_count
    payload = msg.payload.decode('utf-8')
    topic = msg.topic

    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        print("Failed to parse JSON")
        return

    if "headset1" in topic:
        headset1_data = data
        participant = participants[0]
        log_data(participant, "headset1", data)
    elif "headset2" in topic:
        headset2_data = data
        participant = participants[1] if len(participants) > 1 else participants[0]
        log_data(participant, "headset2", data)

    if headset1_data and headset2_data:
        single_mode = False
    else:
        single_mode = True

    if single_mode:
        if headset1_data:
            meditation = headset1_data["meditation"]
            participant = participants[0]
            set_leds(meditation)
            if meditation >= very_high_threshold:
                meditation_count[participant] += 1
                if meditation_count[participant] == 1:
                    check_very_high(participant, "headset1")
            else:
                meditation_count[participant] = 0
    else:
        if headset1_data and headset2_data:
            meditation1 = headset1_data["meditation"]
            meditation2 = headset2_data["meditation"]
            participant1 = participants[0]
            participant2 = participants[1]
            set_leds(meditation1)  # Adjust for specific side LEDs as needed
            set_leds(meditation2)  # Adjust for specific side LEDs as needed
            if meditation1 >= very_high_threshold and meditation2 >= very_high_threshold:
                meditation_count[participant1] += 1
                meditation_count[participant2] += 1
                if meditation_count[participant1] == 1 and meditation_count[participant2] == 1:
                    check_very_high(participant1, "headset1 and headset2")
            else:
                meditation_count[participant1] = 0
                meditation_count[participant2] = 0

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
