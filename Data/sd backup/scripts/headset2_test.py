from rpi_ws281x import PixelStrip, Color

# LED strip configuration
LED_COUNT = 60        # Number of LED pixels.
LED_PIN = 18          # GPIO pin connected to the pixels.
LED_FREQ_HZ = 800000  # LED signal frequency in hertz.
LED_DMA = 10          # DMA channel to use for generating signal.
LED_BRIGHTNESS = 50   # Set brightness (0-255).
LED_INVERT = False    # True to invert the signal.
LED_CHANNEL = 0       # Set to '1' for GPIOs 13, 19, 41, 45 or 53.

# Create NeoPixel object with appropriate configuration.
strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()

# Light up the 60th LED in red
strip.setPixelColor(59, Color(255, 0, 255))  # Red
strip.show()

print("60th LED should be red.")
