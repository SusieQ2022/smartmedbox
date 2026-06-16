# Wiring Guide

> Detailed pin assignments for the Raspberry Pi Zero 2 W. Always power off the
> Pi before changing wiring.

## HX711 weight sensors (×4)

Each HX711 needs a separate data (DT) and clock (SCK) pin pair:

| Compartment | DT (GPIO) | SCK (GPIO) |
|-------------|-----------|------------|
| 0 | GPIO 5  | GPIO 6  |
| 1 | GPIO 13 | GPIO 19 |
| 2 | GPIO 12 | GPIO 16 |
| 3 | GPIO 20 | GPIO 21 |

VCC → 3.3 V, GND → GND (shared rail).

## Reed switches (×4)

Each reed switch connects between a GPIO pin and GND, using the Pi's internal
pull-up resistor:

| Compartment | GPIO |
|-------------|------|
| 0 | GPIO 17 |
| 1 | GPIO 27 |
| 2 | GPIO 22 |
| 3 | GPIO 23 |

## Other components

| Component | Connection |
|-----------|------------|
| PIR motion sensor | OUT → GPIO 24, VCC → 5 V, GND → GND |
| OLED display (I2C) | SDA → GPIO 2, SCL → GPIO 3 |
| Speaker | via I2S DAC or USB audio adapter |
| Camera | CSI ribbon connector |
| Status LEDs | GPIO 25, 8, 7, 1 (with 220 Ω resistors) |

## Safety notes

- Use a common ground rail for all sensors.
- Do not exceed the Pi's 3.3 V logic levels on GPIO inputs.
- Calibrate each load cell after assembly (see `sensors.py` calibration notes).
