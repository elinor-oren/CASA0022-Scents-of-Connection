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
yellowy_white = (255, 255, 100, 0)  # Yellowy white color
tangerine = (255, 80, 0, 0)  # Tangerine orange color
teal = (0, 128, 128, 0)  # Turquoisey blue color
warm_yellow = (255, 150, 0, 0)  # Warm yellow color

# Variables
participant = input("Enter participant number: ")
headset_data = None
meditation_count = 0
start_time = time.time()
very_high_threshold = 81
valid_packets_received = 0  # Counter for received packets with signal strength of 0
experiment_started = False  # Flag to indicate experiment start
rainbow_running = False # Flag to indicate the rainbow led effect
lock = Lock() # Lock to prevent interference between LEDs  

# CSV file setup
csv_file = f'{participant}_headset_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
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
            for i in range(22, 59):
                pixel_index = (i * 256 // num_pixels) + j
                pixels[i] = wheel(pixel_index & 255)
            pixels.show()
            time.sleep(wait)
        rainbow_running = False

""" # This is the teal chaser effect
def gentle_chaser(start, end, color):
    for i in range(start, end):
        pixels[i] = color
        pixels.show()
        time.sleep(0.05)
        pixels[i] = (0, 0, 0, 0)
    pixels.show()
"""

def gentle_chaser(start_led, end_led, color, duration=1, interval=0.01):
    """
    Create a gentle undulating pulsation effect between specified LEDs.
    :param start_led: Starting LED index for the effect
    :param end_led: Ending LED index for the effect
    :param color: Color to use for the effect
    :param duration: Duration of the effect in seconds
    :param interval: Time interval between each step
    """
    steps = int(duration / interval)
    for step in range(steps):
        brightness = (math.sin(step / float(steps) * math.pi * 2) + 1) / 2  # Value between 0 and 1
        for i in range(start_led, end_led + 1):
            if i < num_pixels:
                pixels[i] = tuple(int(brightness * c) for c in color)
        pixels.show()
        time.sleep(interval)

def fixed_low_glow(start, end, color):
    for i in range(start, end):
        pixels[i] = color
    pixels.show()

def set_leds(meditation):
    with lock:
        if rainbow_running:
            return
        pixels.fill((0, 0, 0, 0))  # Clear all LEDs first
    pixels.fill((0, 0, 0, 0))  # Clear all LEDs first
    pixels.show()

    if meditation <= 25:
        gentle_chaser(22, 26, teal)
        gentle_chaser(57, 60, teal)
    elif meditation <= 45:
        fixed_low_glow(22, 26, yellowy_white)
        fixed_low_glow(57, 60, yellowy_white)
        gentle_chaser(27, 30, teal)
        gentle_chaser(53, 56, teal)
    elif meditation <= 65:
        fixed_low_glow(22, 30, yellowy_white)
        fixed_low_glow(53, 60, yellowy_white)
        gentle_chaser(31, 34, teal)
        gentle_chaser(49, 52, teal)
    elif meditation <= 80:
        fixed_low_glow(22, 34, yellowy_white)
        fixed_low_glow(49, 60, yellowy_white)
        gentle_chaser(35, 38, teal)
        gentle_chaser(45, 48, teal)
    else:
        fixed_low_glow(22, 38, yellowy_white)
        fixed_low_glow(45, 60, yellowy_white)
        gentle_chaser(39, 41, teal)
        gentle_chaser(42, 44, teal)

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

    if valid_packets_received >= 3 and not experiment_started:
        experiment_started = True
        log_data("Experiment", "Started")
        blink_leds(1, 1)  # Signal that the experiment has started with a slow blink
       # pixels.fill((0, 0, 0, 0))
       # pixels.show()
        exaggerated_breathing_effect(1, 7)  # Maintain a breathing effect once the experiment has started
        pixels.fill((0, 0, 0, 0))
        pixels.show()

    if headset_data and experiment_started:
        meditation = headset_data["Meditation"]
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
        if valid_packets_received < 3:
            chaser_effect()
        elif experiment_started:
            exaggerated_breathing_effect(1, 7)  # Slow breathing effect after the experiment has started
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()
    client.loop_stop()
    client.disconnect()
