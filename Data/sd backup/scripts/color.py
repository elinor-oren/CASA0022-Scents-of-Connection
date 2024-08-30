import time
import board
import neopixel

# Choose an open pin connected to the Data In of the NeoPixel strip, i.e. board.D18
# NeoPixels must be connected to D10, D12, D18 or D21 to work.
pixel_pin = board.D18

# The number of NeoPixels
num_pixels = 60

# The order of the pixel colors - change to GRBW for RGBW NeoPixels
ORDER = neopixel.GRBW

# Create NeoPixel object with GRBW color ordering
pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=0.2, auto_write=False, pixel_order=ORDER
)

# Define colors
yellowy_white = (255, 255, 100, 0)  # Yellowy white color
tangerine = (255, 80, 0, 0)  # Scarlet burnt orange color
teal = (0, 128, 128, 0)  # Dark turquoise color

def set_colors():
    # Set first 21 LEDs to yellowy white
    for i in range(21):
        pixels[i] = yellowy_white
    
    # Set the next 18 LEDs to scarlet burnt orange
    for i in range(22, 42):
        pixels[i] = tangerine
    
    # Set the remaining 18 LEDs to dark turquoise
    for i in range(42, 60):
        pixels[i] = teal
    
    pixels.show()

while True:
    set_colors()
    time.sleep(1)
