import json
import paho.mqtt.client as mqtt
from rpi_ws281x import PixelStrip, Color
import time

# LED strip configuration:
LED_COUNT = 80        # Number of LED pixels.
LED_PIN = 18          # GPIO pin connected to the pixels (18 supports PWM).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 50   # Set brightness (0-255, where 255 is the brightest)
LED_INVERT = False    # True to invert the signal (if using NPN transistor level shift)
LED_CHANNEL = 0       # Set to '1' for GPIOs 13, 19, 41, 45 or 53

# Create NeoPixel object with appropriate configuration.
strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()

def set_led(headset_id):
    """Light up specific LEDs based on headset ID."""
    # Reset all LEDs first to avoid overlap of old and new states
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0, 0, 0))

    if headset_id == 1:
        # Light up the first LED in green for Headset 1
        strip.setPixelColor(0, Color(0, 255, 0))  # Green
    elif headset_id == 2:
        # Light up the 60th LED in red for Headset 2
        strip.setPixelColor(65, Color(255, 0, 0))  # Red

    strip.show()
    print(f"LED for headset {headset_id} is set.")

def on_connect(client, userdata, flags, rc):
    """Callback for when the client receives a CONNACK response from the server."""
    if rc == 0:
        print("Connected successfully")
        client.subscribe("student/ucbvren/headsets/#")
    else:
        print(f"Failed to connect, return code {rc}\n")

def on_message(client, userdata, msg):
    """Callback for when a PUBLISH message is received from the server."""
    payload = msg.payload.decode('utf-8')
    topic = msg.topic

    if 'headset1' in topic:
        set_led(1)
    elif 'headset2' in topic:
        set_led(2)

# Set up MQTT client
client = mqtt.Client()
client.username_pw_set("student", "ce2021-mqtt-forget-whale")
client.on_connect = on_connect
client.on_message = on_message

# Connect to MQTT broker
client.connect("mqtt.cetools.org", 1884, 60)

# Start the network loop in a separate thread
client.loop_start()

# Keep the script running and ensure cleanup on exit
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    # Clean up the connection and turn off LEDs on interrupt
    client.loop_stop()
    client.disconnect()
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0, 0, 0))
    strip.show()
    strip._cleanup()
