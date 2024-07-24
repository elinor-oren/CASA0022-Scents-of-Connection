# CASA0022-dissertation


Parts list:

- 2 x Mind Flex
- 6 x AAA batteries for the headsets
- 1 x Raspberry Pi 3 (any variety with Bluetooth), with USB cable
- 1 x MicroSD Card 
- 2 x [ESP32](https://wiki.dfrobot.com/FireBeetle_Board_ESP32_E_SKU_DFR0654) boards
- [Flexible LED strip](https://shop.pimoroni.com/products/flexible-rgbw-led-strip-neopixel-ws2812-sk6812-compatible?variant=30260032733267)
- [Ultrasonic Mist Maker](https://www.amazon.co.uk/dp/B0CY2FSGDD?psc=1&ref=ppx_yo2ov_dt_b_product_details)
- [MOSFET](https://cdn.sparkfun.com/datasheets/Components/General/FQP30N06L.pdf)
- 


- 2 x 12" lengths of solid core hookup wire (around #22 or #24 gauge is best).
- Heat gun + Heat shrink tubing
- Solder gun

- Device (PC or Mac) to monitor the serial data and send to MQTT


Software list:

[Arduino Brain Library](https://github.com/kitschpatrol/Brain) 
Optional: Processing Brain Visualizer (download here, it will help to have Processing as well)
Optional (required for the visualizer): controlP5 Processing GUI Library (download here)

[Hardware Tutorial](https://frontiernerds.com/brain-hack)

## Pinout Diagram + Schematic 
### Components Needed
- Raspberry Pi 3
- N-channel MOSFET (e.g., IRLZ44N, IRF540)
- Piezoelectric Ultrasonic Disk
- 10K ohm Resistor 
- Power Supply (matching the voltage requirement of the piezoelectric disk)
- Breadboard and Wires

I extended the wires on the Ultrasonic Atomizer, and I connected to the power pins. 
The 10k ohm resistor is connected between the gate of the MOSFET and ground and acts as a pull-down resistor. It ensures that the MOSFET gate is pulled to a known low state (0V) when the digital pin is not actively driving it. 

Test using the script. Delays must be at least 2000 seconds 

Connect the on/off pins of the button and test on an arduino 





## Setting up the Raspberry Pi 
Follow [this](https://www.tomshardware.com/reviews/raspberry-pi-headless-setup-how-to,6028.html) tutorial 


