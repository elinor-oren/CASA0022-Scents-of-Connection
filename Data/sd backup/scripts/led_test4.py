import json
import paho.mqtt.client as mqtt
import time
import board
import neopixel

# LED strip configuration:
LED_COUNT = 60        # Number of LED pixels.
LED_PIN = board.D18   # GPIO pin connected to the pixels (board.D18 supports PWM).
LED_BRIGHTNESS = 0.2  # Set brightness (0.0 to 1.0, where 1.0 is the brightest)
LED_ORDER = neopixel.RGBW  # Pixel color channel order, change to RGBW if needed

"""
# Configuration for the second strip
LED_COUNT_2 = 60  # Number of LED pixels in the second strip
LED_PIN_2 = board.D13  # GPIO pin connected to the pixels (must support PWM)
LED_ORDER_2 = neopixel.RGBW  # Pixel color channel order for the second strip
"""

# Create NeoPixel object with appropriate configuration.
strip = neopixel.NeoPixel(LED_PIN, LED_COUNT, brightness=LED_BRIGHTNESS, auto_write=False, pixel_order=LED_ORDER)

"""
strip2 = neopixel.NeoPixel(LED_PIN_2, LED_COUNT_2, brightness=0.2, auto_write=False, pixel_order=LED_ORDER_2)
"""


def calculate_leds(meditation_level):
    """Determine number of LEDs to light based on meditation level."""
    """if meditation_level <= 20:
        return 1
    elif meditation_level <= 40:
        return 2
    elif meditation_level <= 60:
        return 3
    elif meditation_level <= 80:
        return 4
    else:
        return 5"""
    led_count = (min(meditation_level // 20, 4) + 1) * 6  # Integer value of meditation level / 20, 4 is the maximum, min function caps it at 5 bins, and each bin corresponds to 6 LEDs
    return led_count


def set_leds( meditation_level, headset_id):
    """Control LEDs based on the meditation level and headset ID."""
    led_count = calculate_leds(meditation_level)  # Calculate number of LEDs based on level

    # Reset LEDs first to avoid overlap of old and new states
    strip.fill((0, 0, 0))

    if headset_id == 1:
        # Light up the first 10 LEDs in green for Headset 1
        color = (0, 255, 0)  # Green
        for i in range(min(30, led_count)):
            strip[i] = color
    elif headset_id == 2:
        # Light up the last 30 LEDs in red for Headset 2
        color = (255, 0, 0)  # Red
        start_index = LED_COUNT 
        for i in range(start_index - min(30, led_count), start_index):
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
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set("student", "ce2021-mqtt-forget-whale")

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
    strip.deinit()  # Properly deinitialize the library to reset the strip
