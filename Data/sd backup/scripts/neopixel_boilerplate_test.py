import time
import board
import neopixel

# Choose an open pin connected to the Data In of the NeoPixel strip, i.e. board.D18
# NeoPixels must be connected to D10, D12, D18 or D21 to work.
pixel_pin = board.D18

# The number of NeoPixels
num_pixels = 60

# The order of the pixel colors - change to RGBW for RGBW NeoPixels
ORDER = neopixel.GRBW

# Create NeoPixel object with RGBW color ordering
pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=0.2, auto_write=False, pixel_order=ORDER
)

def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colors are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        return (0, 0, 0, 0)
    elif pos < 85:
        return (pos * 3, 255 - pos * 3, 0, 0)
    elif pos < 170:
        pos -= 85
        return (255 - pos * 3, 0, pos * 3, 0)
    else:
        pos -= 170
        return (0, pos * 3, 255 - pos * 3, 0)

def rainbow_cycle(wait):
    for j in range(255):
        for i in range(num_pixels):
            pixel_index = (i * 256 // num_pixels) + j
            pixels[i] = wheel(pixel_index & 255)
        pixels.show()
        time.sleep(wait)

while True:
    # Adjust these lines to utilize RGBW color capability
    pixels.fill((255, 0, 0, 0))  # Red with white off
    pixels.show()
    time.sleep(1)

    pixels.fill((0, 255, 0, 0))  # Green with white off
    pixels.show()
    time.sleep(1)

    pixels.fill((0, 0, 255, 0))  # Blue with white off
    pixels.show()
    time.sleep(1)

    # Example to show white color
    pixels.fill((0, 0, 0, 255))  # White only
    pixels.show()
    time.sleep(1)

    rainbow_cycle(0.001)  # Rainbow cycle with 1ms delay per step
