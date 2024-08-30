import json
import paho.mqtt.client as mqtt
import board
import neopixel
import time

# LED strip configuration:
LED_COUNT = 80        # Number of LED pixels.
LED_PIN = board.D18   # GPIO pin connected to the pixels (must support PWM).

# Create NeoPixel object with appropriate configuration.
strip = neopixel.NeoPixel(LED_PIN, LED_COUNT, brightness=0.2, auto_write=False)

def calculate_leds(meditation_level):
    """Determine number of LEDs to light based on meditation level."""
    if meditation_level <= 20:
        return 1
    elif meditation_level <= 40:
        return 2
    elif meditation_level <= 60:
        return 3
    elif meditation_level <= 80:
        return 4
    else:
        return 5

def set_leds(meditation_level, headset_id):
    """Control LEDs based on the meditation level and headset ID."""
    led_count = calculate_leds(meditation_level)  # Calculate number of LEDs based on level

    # Reset LEDs first to avoid overlap of old and new states
    for i in range(len(strip)):
        strip[i] = (0, 0, 0)

    if headset_id == 1:
        # Light up the first 10 LEDs in green for Headset 1
        color = (0, 255, 0)  # Green
        for i in range(min(10, led_count)):  # Ensure we don't exceed 10 LEDs
            strip[i] = color
    elif headset_id == 2:
        # Light up the last 10 LEDs in red for Headset 2
        color = (255, 0, 0)  # Red
        start_index = LED_COUNT - 10  # Start from the last 10th LED
        for i in range(start_index, start_index + min(10, led_count)):  # Ensure we don't exceed 10 LEDs
            strip[i] = color

    strip.show()
    print(f"Illuminating {led_count} LEDs for headset {headset_id} at meditation level {meditation_level}")

def on_connect(client, userdata, flags, rc):
    """Callback for when the client receives a CONNACK response from the server."""
    print(f"Connected with result code {rc}")
    client.subscribe("student/ucbvren/headsets/#")

def on_message(client, userdata, msg):
    """Callback for when a PUBLISH message is received from the server."""
    payload = msg.payload.decode('utf-8')
    topic = msg.topic

    values = payload.split(',')
    if len(values) >= 3:
        try:
            meditation_level = int(values[2])  # Index 2 for meditation value
            if 'headset1' in topic:
                set_leds(meditation_level, 1)
            elif 'headset2' in topic:
                set_leds(meditation_level, 2)
        except ValueError:
            print("Error: Non-integer value found where an integer was expected")
            return
    else:
        print("Error: Incomplete data received")
        return

# Set up MQTT client
client = mqtt.Client()
client.username_pw_set("student", "ce2021-mqtt-forget-whale")
client.on_connect = on_connect
client.on_message = on_message

# Connect to MQTT broker
client.connect("mqtt.cetools.org", 1884, 60)

# Start the network loop in a separate thread
client.loop_start()

# Keep the script running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    # Clean up the connection and GPIO on interrupt
    client.loop_stop()
    client.disconnect()
    for i in range(len(strip)):
        strip[i] = (0, 0, 0)
    strip.show()
