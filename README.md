# CASA0022-dissertation

## Components required:

- 2 x Mind Flex
- 6 x AAA batteries for the headsets
- 2 x 12" lengths of solid core hookup wire (around #22 or #24 gauge is best).
- Heat gun + Heat shrink tubing
- Solder gun

- 1 x Raspberry Pi 3 (any variety with Bluetooth), with USB cable
- 1 x MicroSD Card 
- 2 x [ESP32](https://wiki.dfrobot.com/FireBeetle_Board_ESP32_E_SKU_DFR0654) boards
- [Flexible LED strip](https://shop.pimoroni.com/products/flexible-rgbw-led-strip-neopixel-ws2812-sk6812-compatible?variant=30260032733267)
- [Ultrasonic Mist Maker](https://www.amazon.co.uk/dp/B0CY2FSGDD?psc=1&ref=ppx_yo2ov_dt_b_product_details)
- [MOSFET](https://cdn.sparkfun.com/datasheets/Components/General/FQP30N06L.pdf)
- Piezoelectric Ultrasonic Disk
- 1K ohm Resistor 
- Power Supply (matching the voltage requirement of the piezoelectric disk)
- Breadboard and Wires
- Device (PC or Mac) to monitor the serial data and send to MQTT

## Software required:

Use the [Arduino Brain Library](https://github.com/kitschpatrol/Brain) to capture the raw data as a CSV. 
Optional: Processing Brain Visualizer (download here, it might help to have Processing as well)

## Headset Guide 
[Hardware Tutorial](https://frontiernerds.com/brain-hack)

## Diffuser Guide
### Pinout Diagram  
<img width="800" alt="image" src="https://github.com/user-attachments/assets/09533962-a25a-4786-bbec-89ba633fe305">

I extended the wires on the Ultrasonic Atomizer, and I connected them to the power pins. 

The 1k ohm resistor is connected between the gate of the MOSFET and ground and acts as a pull-down resistor. It ensures that the MOSFET gate is pulled to a known low state (0V) when the digital pin is not actively driving it. 

### 3D Model 
<img width="800" alt="rhino mock-up" src="https://github.com/user-attachments/assets/76588905-08d9-483c-a3fc-3ec6f3cebd6f">

### Setting up the Raspberry Pi 
Follow [this](https://www.tomshardware.com/reviews/raspberry-pi-headless-setup-how-to,6028.html) tutorial

## Connecting the Headset
Update your information and test the MQTT connection from this file. 

