import paho.mqtt.client as mqtt
import json
import time
import RPi.GPIO as GPIO
import csv
from threading import Timer
from datetime import datetime

import board
import neopixel

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)

# NeoPixel setup
pixel_pin = board.D18
num_pixels = 60
ORDER = neopixel.GRBW
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.5, auto_write=False, pixel_order=ORDER)

# Define colors
yellowy_white = (255, 255, 100, 0)  # Yellowy white color
tangerine = (255, 80, 0, 0)  # Tangerine orange color
teal = (0, 128, 128, 0)  # Turquoisey blue color

# Variables
participant = input("Enter participant number: ")
headset_data = None
meditation_count = 0
start_time = time.time()
very_high_threshold = 81
packets_received = 0  # Counter for received packets

# CSV file setup
csv_file = f'{participant}_headset_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
with open(csv_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Timestamp", "Participant", "Headset", "Signal Strength", "Attention", "Meditation", 
                     "Delta", "Theta", "Low Alpha", "High Alpha", "Low Beta", "High Beta", "Low Gamma", "High Gamma", "Very High Time", "Very High Duration"])

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
    pixels.fill((0, 0, 0, 0))  # Turn off all LEDs
    for i in range(led_count):
        pixels[i] = yellowy_white
    pixels.show()

def chaser_effect():
    for i in range(num_pixels):
        pixels.fill((0, 0, 0, 0))
        pixels[i] = teal
        pixels.show()
        time.sleep(0.05)

def check_very_high():
    global meditation_count, start_time
    if meditation_count >= 5:
        GPIO.output(17, GPIO.HIGH)
        duration = time.time() - start_time
        print(f"Very high state achieved in {duration} seconds")
        log_data("Very High Time", duration)
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
    global headset_data, meditation_count, start_time, packets_received
    payload = msg.payload.decode('utf-8')
    topic = msg.topic

    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        print("Failed to parse JSON")
        return

    if "headset1" in topic or "headset2" in topic:
        headset_data = data
        packets_received += 1
        log_data("headset", data)

    if packets_received >= 3:
        log_data("Experiment", "Started")
        set_leds(3)  # Signal that the experiment has started with 3 LEDs
        pixels.fill((0, 0, 0, 0))
        pixels.show()

    if headset_data:
        meditation = headset_data[2]  # Meditation value based on provided order
        set_leds(meditation)
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
        if packets_received < 3 or headset_data is None:
            chaser_effect()
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()
    client.loop_stop()
    client.disconnect()
