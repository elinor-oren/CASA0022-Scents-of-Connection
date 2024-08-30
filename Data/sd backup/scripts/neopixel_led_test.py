import time
import board
import neopixel

# LED strip configuration
LED_COUNT = 60        # Number of LED pixels.
LED_PIN = board.D18   # GPIO pin connected to the pixels (board.D18 supports PWM).
LED_BRIGHTNESS = 0.5  # Set brightness (0.0 to 1.0, where 1.0 is the brightest)
LED_ORDER = neopixel.RGBW  # Pixel color channel order

# Create NeoPixel object with appropriate configuration.
strip = neopixel.NeoPixel(LED_PIN, LED_COUNT, brightness=LED_BRIGHTNESS, auto_write=False, pixel_order=LED_ORDER)

def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(len(strip)):
        strip[i] = color
        strip.show()
        time.sleep(wait_ms / 1000.0)

def theaterChase(strip, color, wait_ms=50, iterations=10):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, len(strip), 3):
                strip[i + q] = color
            strip.show()
            time.sleep(wait_ms / 1000.0)
            for i in range(0, len(strip), 3):
                strip[i + q] = (0, 0, 0)

def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return (pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return (255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return (0, pos * 3, 255 - pos * 3)

def rainbow(strip, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256 * iterations):
        for i in range(len(strip)):
            strip[i] = wheel((i + j) & 255)
        strip.show()
        time.sleep(wait_ms / 1000.0)

def rainbowCycle(strip, wait_ms=20, iterations=5):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256 * iterations):
        for i in range(len(strip)):
            strip[i] = wheel((int(i * 256 / len(strip)) + j) & 255)
        strip.show()
        time.sleep(wait_ms / 1000.0)

def theaterChaseRainbow(strip, wait_ms=50):
    """Rainbow movie theater light style chaser animation."""
    for j in range(256):
        for q in range(3):
            for i in range(0, len(strip), 3):
                strip[i + q] = wheel((i + j) % 255)
            strip.show()
            time.sleep(wait_ms / 1000.0)
            for i in range(0, len(strip), 3):
                strip[i + q] = (0, 0, 0)

# Main program logic follows:
if __name__ == '__main__':
    print('Press Ctrl-C to quit.')
    while True:
        # Color wipe animations
        colorWipe(strip, (255, 0, 0))  # Red color wipe
        colorWipe(strip, (0, 255, 0))  # Green color wipe
        colorWipe(strip, (0, 0, 255))  # Blue color wipe
        # Theater chase animations
        theaterChase(strip, (127, 127, 127))  # White
        # Rainbow animations
        rainbow(strip)
        rainbowCycle(strip)
        theaterChaseRainbow(strip)
